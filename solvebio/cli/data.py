# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from six.moves import input as raw_input

import os
import re
import sys
import gzip
import json
from fnmatch import fnmatch
from collections import defaultdict
import multiprocessing
import signal

import solvebio

from solvebio import Task
from solvebio import Vault
from solvebio import Object
from solvebio import Dataset
from solvebio import DatasetImport
from solvebio import DatasetTemplate
from solvebio import GlobalSearch
from solvebio.utils.files import check_gzip_path
from solvebio.utils.md5sum import md5sum
from solvebio.errors import SolveError
from solvebio.errors import NotFoundError


def should_exclude(path, exclude_paths, dry_run=False, print_logs=True):
    if not exclude_paths:
        return False

    for exclude_path in exclude_paths:

        if fnmatch(path, exclude_path):
            if print_logs:
                print(
                    "{}WARNING: Excluding path {} (via --exclude {})".format(
                        "[Dry Run] " if dry_run else "", path, exclude_path
                    )
                )
            return True

        # An exclude path may be a directory, strip trailing slash and add /*
        # if not already there.
        if not exclude_path.endswith("/*") and fnmatch(
            path, exclude_path.rstrip("/") + "/*"
        ):
            if print_logs:
                print(
                    "{}WARNING: Excluding path {} (via --exclude {})".format(
                        "[Dry Run] " if dry_run else "",
                        path,
                        exclude_path.rstrip("/") + "/*",
                    )
                )
            return True

    return False


def _check_uploaded_folders(base_remote_path, local_start, all_folders):
    """Identifies which remote folders already exist so that we can optimize
    which folders to create in the upload workflow.

    Note, due to the asynchronous nature of GlobalSearch, returned folders
    may sometimes already exist. A subsequent exact check is required before
    uploading (as implemented in `Object.create_folder`).

    Args:
        base_remote_path: Base remote parent folder full path to upload to.
        local_start: The name of the base folder to upload.
        all_folders: A list of remote folders to potentially create in full path format.
    Returns:
        all_folder_parts (set): A unique set of folder parts to create that do
            not already exist.

    """
    upload_root_path, _ = Object.validate_full_path(
        os.path.join(base_remote_path, local_start)
    )
    results = GlobalSearch().filter(path__prefix=upload_root_path, type="folder")
    remote_folders_existing = set([x.full_path for x in results])
    all_folder_parts = set()
    for vault, remote_folder_path in all_folders:
        subfolders = remote_folder_path.lstrip("/").split("/")
        parent_folder_path = subfolders[0]
        # Split each folder into parts and check if these exist
        # Skip root folder as we don't need to create this
        for folder in subfolders[1:]:
            folder_full_path = os.path.join(parent_folder_path, folder)
            if folder_full_path not in remote_folders_existing:
                all_folder_parts.add(folder_full_path)
            parent_folder_path = folder_full_path

    return all_folder_parts


def _upload_folder(
    domain,
    vault,
    base_remote_path,
    base_local_path,
    local_start,
    exclude_paths=None,
    dry_run=False,
    num_processes=1,
    archive_folder=None
):
    all_folders = []
    all_files = []

    # Create the upload root folder if it does not exist on the remote
    try:
        upload_root_path, _ = Object.validate_full_path(
            os.path.join(base_remote_path, local_start)
        )
        Object.get_by_full_path(upload_root_path, assert_type="folder")
    except NotFoundError:
        base_remote_path, path_dict = Object.validate_full_path(base_remote_path)
        base_folder_path = os.path.join(base_remote_path, local_start)
        if dry_run:
            print("[Dry Run] Creating folder {}".format(base_folder_path))
        else:
            all_folders.append((vault, base_folder_path))

    # Create folders and upload files
    for abs_local_parent_path, folders, files in os.walk(base_local_path):
        # Strips off the local path and adds the parent directory at
        # each phase of the loop
        local_parent_path = re.sub(
            "^" + os.path.dirname(base_local_path), "", abs_local_parent_path
        ).lstrip("/")

        if should_exclude(abs_local_parent_path, exclude_paths, dry_run=dry_run):
            continue

        remote_folder_full_path = os.path.join(base_remote_path, local_parent_path)

        # Create folders
        for folder in folders:
            new_folder_path = os.path.join(abs_local_parent_path, folder)
            if should_exclude(new_folder_path, exclude_paths, dry_run=dry_run):
                continue

            remote_path = os.path.join(remote_folder_full_path, folder)
            all_folders.append((vault, remote_path))

        # Upload the files that do not yet exist on the remote
        for f in files:
            local_file_path = os.path.join(abs_local_parent_path, f)
            if should_exclude(local_file_path, exclude_paths, dry_run=dry_run):
                continue
            all_files.append((local_file_path, remote_folder_full_path, vault.full_path, dry_run, archive_folder))

    if num_processes > 1:
        # Only perform optimization if parallelization is requested by the user
        all_folder_parts = _check_uploaded_folders(base_remote_path, local_start, all_folders)
    else:
        all_folder_parts = set([x[1] for x in all_folders])

    # Create folders serially since these require
    # previous folders to be created so that parent_object_id can
    # be populated
    all_folder_parts = sorted(all_folder_parts, key=lambda x: len(x.split("/")))
    for folder in all_folder_parts:
        print("{}Creating folder {}".format(
            "[Dry Run] " if dry_run else "", folder))
        Object.create_folder(vault, folder)

    # Create files in parallel
    # Signal handling allows for graceful exit upon KeyboardInterrupt
    original_sigint_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
    pool = multiprocessing.Pool(num_processes)
    signal.signal(signal.SIGINT, original_sigint_handler)
    try:
        for result in pool.imap_unordered(_create_file_job, all_files):
            # Check if an exception was raised by the pool worker
            if isinstance(result, Exception):
                raise result
    except KeyboardInterrupt:
        print("Caught KeyboardInterrupt, terminating workers and cancelling upload.")
        pool.terminate()
    else:
        pool.close()


def _create_file_job(args):
    """Uploads a single file from local storage to EDP. Args are
    packed into a single tuple to facilitate multiprocessing.

    Args:
        args[0] (local_file_path): Path to local file.
        args[1] (remote_folder_path): Path to remote parent folder.
        args[2] (vault_path): Path to remote vault.
        args[3] (dry_run): Whether to performa dry run.
    Returns:
        None or Exception if exception is raised.
    """
    try:
        local_file_path, remote_folder_full_path, vault_path, dry_run, archive_folder = args
        if dry_run:
            print("[Dry Run] Uploading {} to {}".format(
                local_file_path, remote_folder_full_path))
            return
        remote_parent = Object.get_by_full_path(
            remote_folder_full_path, assert_type="folder"
        )
        Object.upload_file(local_file_path, remote_parent.path, vault_path, archive_folder=archive_folder)
        return
    except KeyboardInterrupt as e:
        raise e
    except Exception as e:
        return e


def _create_template_from_file(template_file, dry_run=False):
    mode = "r"
    fopen = open
    if check_gzip_path(template_file):
        mode = "rb"
        fopen = gzip.open

    # Validate the template file
    with fopen(template_file, mode) as fp:
        try:
            template_json = json.load(fp)
        except:
            print(
                "Template file {0} could not be loaded. Please "
                "pass valid JSON".format(template_file)
            )
            sys.exit(1)

    if dry_run:
        template = DatasetTemplate(**template_json)
        print("A new dataset template will be created from: {0}".format(template_file))
    else:
        template = DatasetTemplate.create(**template_json)
        print("A new dataset template was created with id: {0}".format(template.id))

    return template


def create_dataset(args, template=None):
    """
    Attempt to create a new dataset given the following params:

        * template_id
        * template_file
        * capacity
        * tag
        * metadata
        * metadata_json_file
        * create_vault
        * full_path
        * dry_run
    """
    if args.dry_run:
        print("NOTE: Running create-dataset command in dry run mode")

    full_path, path_dict = Object.validate_full_path(args.full_path)

    try:
        # Fail if a dataset already exists.
        Object.get_by_full_path(full_path, assert_type="dataset")
        print("A dataset already exists at path: {0}".format(full_path))
        sys.exit(1)
    except NotFoundError:
        pass

    # Accept a template_id or a template_file
    if template:
        # Template has already been validated/created
        # in the import command that called this
        pass
    elif args.template_id:
        try:
            template = DatasetTemplate.retrieve(args.template_id)
        except SolveError as e:
            if e.status_code != 404:
                raise e
            print("No template with ID {0} found!".format(args.template_id))
            sys.exit(1)
    elif args.template_file:
        template = _create_template_from_file(args.template_file, args.dry_run)
    else:
        template = None

    if template:
        print(
            "Creating new dataset {0} using the template '{1}'.".format(
                full_path, template.name
            )
        )
        fields = template.fields
        description = "Created with dataset template: {0}".format(str(template.id))
    else:
        fields = []
        description = None

    # Create dataset metadata
    # Looks at --metadata_json_file first and will update
    # that with any other key/value pairs passed in to --metadata
    metadata = {}
    if args.metadata and args.metadata_json_file:
        print(
            "WARNING: Received --metadata and --metadata-json-file. "
            "Will update the JSON file values with the --metadata values"
        )

    if args.metadata_json_file:
        with open(args.metadata_json_file, "r") as fp:
            try:
                metadata = json.load(fp)
            except:
                print(
                    "Metadata JSON file {0} could not be loaded. Please "
                    "pass valid JSON".format(args.metadata_json_file)
                )
                sys.exit(1)

    if args.metadata:
        metadata.update(args.metadata)

    if args.dry_run:
        print(
            "Creating new '{}' capacity dataset at {}".format(args.capacity, full_path)
        )
        if description:
            print("Description: {}".format(description))
        if fields:
            print("Fields: {}".format(fields))
        if args.tag:
            print("Tags: {}".format(args.tag))
        if metadata:
            print("Metadata: {}".format(metadata))
        return

    return Dataset.get_or_create_by_full_path(
        full_path,
        capacity=args.capacity,
        fields=fields,
        description=description,
        tags=args.tag or [],
        metadata=metadata,
        create_vault=args.create_vault,
    )


def upload(args):
    """
    Given a folder or file, upload all the folders and files contained
    within it, skipping ones that already exist on the remote.
    """

    base_remote_path, path_dict = Object.validate_full_path(args.full_path)

    # Assert the vault exists and is accessible
    vault = Vault.get_by_full_path(path_dict["vault_full_path"])

    # If not the vault root, validate remote path exists and is a folder
    if path_dict["path"] != "/":
        try:
            Object.get_by_full_path(base_remote_path, assert_type="folder")
        except:
            if not args.create_full_path:
                raise

            if args.dry_run:
                print("[Dry Run] Creating {}".format(base_remote_path))
            else:
                # Create the destination path (including subfolders)
                # if not found
                parent_folder_path = vault.full_path + ":"
                folders = path_dict["path"].lstrip("/").split("/")
                for folder in folders:
                    folder_full_path = os.path.join(parent_folder_path, folder)
                    parent_folder = Object.create_folder(vault, folder_full_path)
                    parent_folder_path = parent_folder.full_path

    # Exit if there are multiple local paths and the
    # exclude paths are not absolute
    base_exclude_paths = args.exclude or []
    if base_exclude_paths and len(args.local_path) > 1:
        rel_exclude_paths = [p for p in base_exclude_paths if not os.path.isabs(p)]
        local_path_parents = set(
            [os.path.dirname(os.path.abspath(p)) for p in args.local_path]
        )
        if rel_exclude_paths and len(local_path_parents) > 1:
            sys.exit(
                "Exiting. Cannot apply the --exclude relative paths when "
                "multiple upload paths with different parent directories "
                "are specified. Make --exclude paths absolute or run "
                "upload paths one at a time."
            )

    for local_path in args.local_path:

        # Expand local path and strip trailing slash
        local_path = os.path.abspath(local_path).rstrip("/")
        local_name = os.path.basename(local_path)

        # add basepath to excludes
        exclude_paths = [
            os.path.join(local_path, os.path.normpath(exclude_path))
            for exclude_path in base_exclude_paths
        ]

        if os.path.isdir(local_path):
            _upload_folder(
                path_dict["domain"],
                vault,
                base_remote_path,
                local_path,
                local_name,
                exclude_paths=exclude_paths,
                dry_run=args.dry_run,
                num_processes=args.num_processes,
                archive_folder=args.archive_folder
            )
        else:
            if args.dry_run:
                print(
                    "[Dry Run] Uploading {} to {}".format(local_path, path_dict["path"])
                )
            else:
                Object.upload_file(local_path, path_dict["path"], vault.full_path, archive_folder=args.archive_folder)


def import_file(args):
    """
    Given a dataset and a local path, upload and import the file(s).

    Command arguments (args):

        * create_dataset and it's args
            * capacity
            * template_id
            * template_file
            * capacity
            * tag
            * metadata
            * metadata_json_file
            * create_vault
        * full_path
        * commit_mode
        * remote_source
        * dry_run
        * follow
        * file (list)

    """
    if args.dry_run:
        print("NOTE: Running import command in dry run mode")

    full_path, path_dict = Object.validate_full_path(args.full_path)

    files_list = []
    if args.remote_source:
        # Validate files
        for file_fp in args.file:
            files_ = list(Object.all(glob=file_fp, limit=1000))
            if not files_:
                print(
                    "Did not find any {}files at path {}".format(
                        "remote " if args.remote_source else "", file_fp
                    )
                )
            else:
                for file_ in files_:
                    print("Found file: {}".format(file_.full_path))
                    files_list.append(file_)

    else:
        # Local files
        # Note: if these are globs or folders, then this will
        # create a multi-file manifest which is deprecated
        # and should be updated to one file per import.
        files_list = [fp for fp in args.file]

    if not files_list:
        print(
            "Exiting. No files were found at the following {}paths: {}".format(
                "remote " if args.remote_source else "", ", ".join(args.file)
            )
        )
        sys.exit(1)

    if args.template_id:
        try:
            template = DatasetTemplate.retrieve(args.template_id)
        except SolveError as e:
            if e.status_code != 404:
                raise e
            print("No template with ID {0} found!".format(args.template_id))
            sys.exit(1)
    elif args.template_file:
        template = _create_template_from_file(args.template_file, args.dry_run)
    else:
        template = None

    # Ensure the dataset exists. Create if necessary.
    if args.create_dataset:
        dataset = create_dataset(args, template=template)
    else:
        try:
            dataset = Object.get_by_full_path(full_path, assert_type="dataset")
        except solvebio.errors.NotFoundError:
            print("Dataset not found: {0}".format(full_path))
            print("Tip: use the --create-dataset flag " "to create one from a template")
            sys.exit(1)

    if args.dry_run:
        print("Importing the following files/paths into dataset: {}".format(full_path))
        for file_ in files_list:
            if args.remote_source:
                print(file_.full_path)
            else:
                print(file_)
        return

    # Generate a manifest from the local files
    imports = []
    for file_ in files_list:
        if args.remote_source:
            kwargs = dict(object_id=file_.id)
        else:
            manifest = solvebio.Manifest()
            manifest.add(file_)
            kwargs = dict(manifest=manifest.manifest)

        # Add template params
        if template:
            kwargs.update(template.import_params)

        # Create the import
        import_ = DatasetImport.create(
            dataset_id=dataset.id, commit_mode=args.commit_mode, **kwargs
        )

        imports.append(import_)

    if args.follow:
        dataset.activity(follow=True)
    else:
        mesh_url = "https://my.solvebio.com/activity/"
        print("Your import has been submitted, view details at: {0}".format(mesh_url))

    return imports, dataset


def download(args):
    """
    Given a folder or file, download all the files contained
    within it (not recursive).
    """
    return _download(
        args.full_path,
        args.local_path,
        dry_run=args.dry_run,
        recursive=args.recursive,
        excludes=args.exclude,
        includes=args.include,
        delete=args.delete,
    )


def _download(
    full_path,
    local_folder_path,
    dry_run=False,
    recursive=False,
    excludes=[],
    includes=[],
    delete=False,
):
    """
    Given a folder or file, download all the files contained
    within it.
    """
    if dry_run:
        print("Running in dry run mode. Not downloading any files.")

    local_folder_path = os.path.expanduser(local_folder_path)
    if not os.path.exists(local_folder_path):
        print("Creating local download folder {}".format(local_folder_path))
        if not dry_run:
            if not os.path.exists(local_folder_path):
                os.makedirs(local_folder_path)

    if recursive:
        _download_recursive(
            full_path, local_folder_path, dry_run, excludes, includes, delete
        )
        return

    # API will determine depth based on number of "/" in the glob
    # Add */** to match in any vault (recursive)
    files = Object.all(glob=full_path, limit=1000, object_type="file")
    if not files:
        print(
            "No file(s) found at --full-path {}\nIf attempting to download "
            "multiple files, try using a glob 'vault:/path/folder/*'".format(full_path)
        )

    for file_ in files:

        if not dry_run:
            file_.download(local_folder_path)

        print(
            "Downloaded: {} to {}/{}".format(
                file_.full_path, local_folder_path, file_.filename
            )
        )


def _download_recursive(
    full_path, local_folder_path, dry_run=False, excludes=[], includes=[], delete=False
):

    if "**" in full_path:
        raise Exception(
            "Paths containing ** are not compatible with the --recursive flag."
        )

    full_path, parts = Object.validate_full_path(full_path)
    results = GlobalSearch().filter(path__prefix=full_path)
    num_files = len([x for x in results if x.get("object_type") == "file"])
    print("Found {} files to download.".format(num_files))
    if num_files == 0:
        if full_path.endswith("/*"):
            print(
                "Folder names ending with '/*' are not supported with "
                "the --recursive flag, try again with only the folder name."
            )
        return

    remote_objects = []
    for file_obj in results:
        depth = len(file_obj.path.split("/"))
        file_obj.depth = depth
        # MD5 not retrieved by GlobalSearch so
        # separate API call is needed
        if file_obj.is_file:
            file_obj = Object.retrieve(file_obj.id)
        file_obj.depth = depth
        remote_objects.append(file_obj)

    min_depth = min([x.depth for x in remote_objects])
    num_at_min_depth = len([x for x in remote_objects if x.depth == min_depth])
    if num_at_min_depth == 1:
        base_folder_depth = min_depth
    else:
        base_folder_depth = min_depth - 1

    downloaded_files = set()

    remote_files = [x for x in remote_objects if x.get("object_type") == "file"]
    for remote_file in remote_files:
        rel_parts = remote_file.path.split("/")[base_folder_depth:]
        relative_file_path = os.path.join(*rel_parts)
        local_path = os.path.join(local_folder_path, relative_file_path)

        # Skip over files that are excluded (not recovered by include)
        if should_exclude(
            local_path, excludes, print_logs=False
        ) and not should_exclude(local_path, includes, print_logs=False):
            continue

        # Keep track of remote files to delete locally
        downloaded_files.add(os.path.abspath(local_path))

        # Skip over files that match remote md5 checksum
        if os.path.exists(local_path):
            remote_md5 = remote_file.get("md5")
            if remote_md5 and remote_md5 == md5sum(local_path)[0]:
                print("Skipping {} already in sync".format(local_path))
                continue

        parent_dir = os.path.dirname(local_path)
        print(
            "{}Downloading file {}".format("[Dry run] " if dry_run else "", local_path)
        )
        if not dry_run:
            os.makedirs(parent_dir, exist_ok=True)
            remote_file.download(local_path)

    if not delete:
        return
    print("[Warning] Deleting local files not found in remote vault")
    for root, folders, files in os.walk(local_folder_path):
        for file_ in files:
            local_abs_path = os.path.abspath(os.path.join(root, file_))
            if local_abs_path in downloaded_files:
                continue
            print(
                "{}Deleting file {}".format(
                    "[Dry run] " if dry_run else "", local_abs_path
                )
            )
            if not dry_run:
                os.remove(local_abs_path)

        for folder in folders:
            local_abs_path = os.path.abspath(os.path.join(root, folder))
            if len(os.listdir(local_abs_path)) == 0:
                print(
                    "{}Deleting folder {}".format(
                        "[Dry run] " if dry_run else "", local_abs_path
                    )
                )
                os.rmdir(local_abs_path)


def ls(args):
    """
    Given a SolveBio remote path, list the files and folders
    """
    return _ls(args.full_path)


def _ls(full_path):

    if "**" in full_path:
        print("Recursive paths containing ** are not supported by `ls`")
        return

    files = list(Object.all(glob=full_path, limit=1000))
    if len(files) == 1 and files[0].is_folder:
        files = Object.all(glob=files[0].full_path + "/*")
    for file_ in files:
        print(
            "{}  {}  {}".format(
                file_.last_modified, file_.object_type.ljust(8), file_.full_path
            )
        )

    if len(files) == 0:
        print(
            "No file(s) found at --full-path {}, "
            'try using a glob instead:  "vault:/path/folder/*'.format(full_path)
        )


def should_tag_by_object_type(args, object_):
    """Returns True if object matches object type requirements"""
    valid = True
    if args.tag_folders_only and not object_.is_folder:
        valid = False

    if args.tag_files_only and not object_.is_file:
        valid = False

    if args.tag_datasets_only and not object_.is_dataset:
        valid = False

    if not valid:
        print(
            "{}WARNING: Excluding {} {} by object_type".format(
                "[Dry Run] " if args.dry_run else "",
                object_.object_type,
                object_.full_path,
            )
        )

    return valid


def tag(args):
    """Tags a list of paths with provided tags"""

    objects = []
    for full_path in args.full_path:
        # API will determine depth based on number of "/" in the glob
        # Add */** to match in any vault (recursive)
        objects.extend(list(Object.all(glob=full_path, permission="write", limit=1000)))

    seen_vaults = {}
    taggable_objects = []
    exclusions = args.exclude or []

    # Runs through all objects to get tagging candidates
    # taking exclusions and object_type filters into account.
    for object_ in objects:

        if should_exclude(object_.full_path, exclusions, dry_run=args.dry_run):
            continue

        if should_tag_by_object_type(args, object_):
            taggable_objects.append(object_)
            seen_vaults[object_.vault_id] = 1

    if not taggable_objects:
        print("No taggable objects found at provided locations.")
        return

    # If args.no_input, changes will be applied immediately.
    # Otherwise, prints the objects and if tags will be applied or not
    for object_ in taggable_objects:
        object_.tag(
            args.tag, remove=args.remove, dry_run=args.dry_run, apply_save=args.no_input
        )

    # Prompts for confirmation and then runs with apply_save=True
    if not args.no_input:

        print("")
        res = raw_input(
            "Are you sure you want to apply the above changes to "
            "{} object(s) in {} vault(s)? [y/N] ".format(
                len(taggable_objects), len(seen_vaults.keys())
            )
        )
        print("")
        if res.strip().lower() != "y":
            print("Not applying changes.")
            return

        for object_ in taggable_objects:
            object_.tag(
                args.tag, remove=args.remove, dry_run=args.dry_run, apply_save=True
            )


def show_queue(args):
    """Show running and queued tasks"""
    queue()


def queue(statuses=["running", "queued"]):
    """
    Get all running and queued Tasks for an account
    and groups them by User and status.
    It also prints out the Job queue in the order that they
    will be evaluated.
    """
    task_map = {}
    tasks = Task.all(status=",".join(statuses))
    for task in tasks:
        if task.user.id not in task_map:
            task_map[task.user.id] = []

        task_map[task.user.id].append(task)

    if not task_map:
        print("No running or queued tasks in your account!")
        return

    print("##" * 10)
    print("# Tasks by User")
    print("##" * 10)
    for tasks in task_map.values():
        user = tasks[0].user
        status_map = defaultdict(int)
        print("{} Tasks ({})".format(len(tasks), user.full_name))
        for task in tasks:
            status_map[task.status] += 1

        for status, cnt in status_map.items():
            if cnt:
                print("\t{} are {}".format(cnt, status))
