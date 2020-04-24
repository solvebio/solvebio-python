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

import solvebio

from solvebio import Task
from solvebio import Vault
from solvebio import Object
from solvebio import Dataset
from solvebio import DatasetImport
from solvebio import DatasetTemplate
from solvebio.utils.files import check_gzip_path
from solvebio.errors import SolveError
from solvebio.errors import NotFoundError


def _create_folder(vault, full_path, tags=None):
    """Create a folder if not exists"""
    full_path, path_dict = \
        Object.validate_full_path(full_path)
    folder_name = path_dict['filename']

    try:
        new_obj = Object.get_by_full_path(full_path)
        if not new_obj.is_folder:
            raise SolveError('Object type {} already exists at location: {}'
                             .format(new_obj.object_type, full_path))
    except NotFoundError:
        # Create the folder
        if path_dict['parent_path'] == '/':
            parent_object_id = None
        else:
            parent = Object.get_by_full_path(path_dict['parent_full_path'],
                                             assert_type='folder')
            parent_object_id = parent.id

        # Make the API call
        new_obj = Object.create(
            vault_id=vault.id,
            parent_object_id=parent_object_id,
            object_type='folder',
            filename=folder_name,
            tags=tags or []
        )

        print('Notice: Folder created for {0} at {1}'
              .format(folder_name, new_obj.path))

    return new_obj


def should_exclude(path, exclude_paths, dry_run=False):
    if not exclude_paths:
        return False

    for exclude_path in exclude_paths:

        if fnmatch(path, exclude_path):
            print("{}WARNING: Excluding path {} (via --exclude {})"
                  .format('[Dry Run] ' if dry_run else '', path, exclude_path))
            return True

        # An exclude path may be a directory, strip trailing slash and add /*
        # if not already there.
        if not exclude_path.endswith('/*') and \
                fnmatch(path, exclude_path.rstrip('/') + '/*'):
            print("{}WARNING: Excluding path {} (via --exclude {})"
                  .format('[Dry Run] ' if dry_run else '',
                          path, exclude_path.rstrip('/') + '/*'))
            return True

    return False


def _upload_folder(domain, vault, base_remote_path, base_local_path,
                   local_start, exclude_paths=None, dry_run=False):

    # Create the upload root folder if it does not exist on the remote
    try:
        upload_root_path, _ = Object.validate_full_path(
            os.path.join(base_remote_path, local_start)
        )
        Object.get_by_full_path(upload_root_path, assert_type='folder')
    except NotFoundError:
        base_remote_path, path_dict = \
            Object.validate_full_path(base_remote_path)
        base_folder_path = os.path.join(base_remote_path, local_start)
        if dry_run:
            print('[Dry Run] Creating folder {}'.format(base_folder_path))
        else:
            _create_folder(vault, base_folder_path)

    # Create folders and upload files
    for abs_local_parent_path, folders, files in os.walk(base_local_path):

        # Strips off the local path and adds the parent directory at
        # each phase of the loop
        local_parent_path = re.sub(
            '^' + os.path.dirname(base_local_path), '', abs_local_parent_path
        ).lstrip('/')

        if should_exclude(abs_local_parent_path, exclude_paths,
                          dry_run=dry_run):
            continue

        remote_folder_full_path = \
            os.path.join(base_remote_path, local_parent_path)

        # Create folders
        for folder in folders:
            new_folder_path = os.path.join(abs_local_parent_path, folder)
            if should_exclude(new_folder_path, exclude_paths,
                              dry_run=dry_run):
                continue

            remote_path = os.path.join(remote_folder_full_path, folder)
            if dry_run:
                print('[Dry Run] Creating folder {}'.format(remote_path))
            else:
                _create_folder(vault, remote_path)

        # Upload the files that do not yet exist on the remote
        for f in files:
            local_file_path = os.path.join(abs_local_parent_path, f)
            if should_exclude(local_file_path, exclude_paths, dry_run=dry_run):
                continue

            if dry_run:
                print('[Dry Run] Uploading {} to {}'
                      .format(local_file_path, remote_folder_full_path))
            else:
                remote_parent = Object.get_by_full_path(
                    remote_folder_full_path, assert_type='folder')
                Object.upload_file(local_file_path, remote_parent.path,
                                   vault.full_path)


def _create_template_from_file(template_file, dry_run=False):
    mode = 'r'
    fopen = open
    if check_gzip_path(template_file):
        mode = 'rb'
        fopen = gzip.open

    # Validate the template file
    with fopen(template_file, mode) as fp:
        try:
            template_json = json.load(fp)
        except:
            print('Template file {0} could not be loaded. Please '
                  'pass valid JSON'.format(template_file))
            sys.exit(1)

    if dry_run:
        template = DatasetTemplate(**template_json)
        print("A new dataset template will be created from: {0}"
              .format(template_file))
    else:
        template = DatasetTemplate.create(**template_json)
        print("A new dataset template was created with id: {0}"
              .format(template.id))

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
        Object.get_by_full_path(full_path, assert_type='dataset')
        print('A dataset already exists at path: {0}'.format(full_path))
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
        print("Creating new dataset {0} using the template '{1}'."
              .format(full_path, template.name))
        fields = template.fields
        description = 'Created with dataset template: {0}' \
            .format(str(template.id))
    else:
        fields = []
        description = None

    # Create dataset metadata
    # Looks at --metadata_json_file first and will update
    # that with any other key/value pairs passed in to --metadata
    metadata = {}
    if args.metadata and args.metadata_json_file:
        print('WARNING: Received --metadata and --metadata-json-file. '
              'Will update the JSON file values with the --metadata values')

    if args.metadata_json_file:
        with open(args.metadata_json_file, 'r') as fp:
            try:
                metadata = json.load(fp)
            except:
                print('Metadata JSON file {0} could not be loaded. Please '
                      'pass valid JSON'.format(args.metadata_json_file))
                sys.exit(1)

    if args.metadata:
        metadata.update(args.metadata)

    if args.dry_run:
        print("Creating new '{}' capacity dataset at {}"
              .format(args.capacity, full_path))
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
    vault = Vault.get_by_full_path(path_dict['vault_full_path'])

    # If not the vault root, validate remote path exists and is a folder
    if path_dict['path'] != '/':
        try:
            Object.get_by_full_path(base_remote_path, assert_type='folder')
        except:
            if not args.create_full_path:
                raise

            if args.dry_run:
                print('[Dry Run] Creating {}'.format(base_remote_path))
            else:
                # Create the destination path (including subfolders)
                # if not found
                parent_folder_path = vault.full_path + ':'
                folders = path_dict['path'].lstrip('/').split('/')
                for folder in folders:
                    folder_full_path = os.path.join(parent_folder_path, folder)
                    parent_folder = _create_folder(vault, folder_full_path)
                    parent_folder_path = parent_folder.full_path

    # Exit if there are multiple local paths and the
    # exclude paths are not absolute
    base_exclude_paths = args.exclude or []
    if base_exclude_paths and len(args.local_path) > 1:
        rel_exclude_paths = [p for p in base_exclude_paths
                             if not os.path.isabs(p)]
        local_path_parents = set([os.path.dirname(os.path.abspath(p))
                                  for p in args.local_path])
        if rel_exclude_paths and len(local_path_parents) > 1:
            sys.exit('Exiting. Cannot apply the --exclude relative paths when '
                     'multiple upload paths with different parent directories '
                     'are specified. Make --exclude paths absolute or run '
                     'upload paths one at a time.')

    for local_path in args.local_path:

        # Expand local path and strip trailing slash
        local_path = os.path.abspath(local_path).rstrip('/')
        local_name = os.path.basename(local_path)

        # add basepath to excludes
        exclude_paths = [
            os.path.join(local_path, os.path.normpath(exclude_path))
            for exclude_path in base_exclude_paths
        ]

        if os.path.isdir(local_path):
            _upload_folder(path_dict['domain'], vault,
                           base_remote_path, local_path,
                           local_name, exclude_paths=exclude_paths,
                           dry_run=args.dry_run)
        else:
            if args.dry_run:
                print('[Dry Run] Uploading {} to {}'
                      .format(local_path, path_dict['path']))
            else:
                Object.upload_file(local_path, path_dict['path'],
                                   vault.full_path)


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
                print("Did not find any {}files at path {}".format(
                    'remote ' if args.remote_source else '', file_fp))
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
        print("Exiting. No files were found at the following {}paths: {}"
              .format('remote ' if args.remote_source else '',
                      ', '.join(args.file)))
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
            dataset = Object.get_by_full_path(full_path, assert_type='dataset')
        except solvebio.errors.NotFoundError:
            print("Dataset not found: {0}".format(full_path))
            print("Tip: use the --create-dataset flag "
                  "to create one from a template")
            sys.exit(1)

    if args.dry_run:
        print("Importing the following files/paths into dataset: {}"
              .format(full_path))
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
            dataset_id=dataset.id,
            commit_mode=args.commit_mode,
            **kwargs
        )

        imports.append(import_)

    if args.follow:
        dataset.activity(follow=True)
    else:
        mesh_url = 'https://my.solvebio.com/activity/'
        print("Your import has been submitted, view details at: {0}"
              .format(mesh_url))

    return imports, dataset


def download(args):
    """
    Given a folder or file, download all the files contained
    within it (not recursive).
    """
    return _download(args.full_path, args.local_path, dry_run=args.dry_run)


def _download(full_path, local_folder_path, dry_run=False):
    """
    Given a folder or file, download all the files contained
    within it (not recursive).
    """
    if dry_run:
        print('Running in dry run mode. Not downloading any files.')

    local_folder_path = os.path.expanduser(local_folder_path)
    if not os.path.exists(local_folder_path):
        print("Creating local download folder {}".format(local_folder_path))
        if not dry_run:
            if not os.path.exists(local_folder_path):
                os.makedirs(local_folder_path)

    # API will determine depth based on number of "/" in the glob
    # Add */** to match in any vault (recursive)
    files = Object.all(glob=full_path, limit=1000, object_type='file')
    if not files:
        print("No file(s) found at --full-path {}\nIf attempting to download "
              "multiple files, try using a glob 'vault:/path/folder/*'"
              .format(full_path))

    for file_ in files:

        if not dry_run:
            file_.download(local_folder_path)

        print('Downloaded: {} to {}/{}'.format(
            file_.full_path, local_folder_path, file_.filename))


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
        print("{}WARNING: Excluding {} {} by object_type".format(
            '[Dry Run] ' if args.dry_run else '',
            object_.object_type, object_.full_path))

    return valid


def tag(args):
    """Tags a list of paths with provided tags"""

    objects = []
    for full_path in args.full_path:
        # API will determine depth based on number of "/" in the glob
        # Add */** to match in any vault (recursive)
        objects.extend(list(Object.all(
            glob=full_path, permission='write', limit=1000)))

    seen_vaults = {}
    taggable_objects = []
    exclusions = args.exclude or []

    # Runs through all objects to get tagging candidates
    # taking exclusions and object_type filters into account.
    for object_ in objects:

        if should_exclude(object_.full_path, exclusions,
                          dry_run=args.dry_run):
            continue

        if should_tag_by_object_type(args, object_):
            taggable_objects.append(object_)
            seen_vaults[object_.vault_id] = 1

    if not taggable_objects:
        print('No taggable objects found at provided locations.')
        return

    # If args.no_input, changes will be applied immediately.
    # Otherwise, prints the objects and if tags will be applied or not
    for object_ in taggable_objects:
        object_.tag(
            args.tag, remove=args.remove,
            dry_run=args.dry_run, apply_save=args.no_input)

    # Prompts for confirmation and then runs with apply_save=True
    if not args.no_input:

        print('')
        res = raw_input(
            'Are you sure you want to apply the above changes to '
            '{} object(s) in {} vault(s)? [y/N] '
            .format(len(taggable_objects), len(seen_vaults.keys()))
        )
        print('')
        if res.strip().lower() != 'y':
            print('Not applying changes.')
            return

        for object_ in taggable_objects:
            object_.tag(
                args.tag, remove=args.remove,
                dry_run=args.dry_run, apply_save=True)


def show_queue(args):
    """Show running and queued tasks"""
    queue()


def queue(statuses=['running', 'queued']):
    """
    Get all running and queued Tasks for an account
    and groups them by User and status.
    It also prints out the Job queue in the order that they
    will be evaluated.
    """
    task_map = {}
    tasks = Task.all(status=','.join(statuses))
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
