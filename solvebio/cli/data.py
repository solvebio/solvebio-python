# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function

import os
import re
import sys
import gzip
import json

import solvebio

from solvebio import Vault
from solvebio import Object
from solvebio.utils.files import check_gzip_path
from solvebio.errors import NotFoundError


def _create_folder(vault, full_path, tags=None):
    """Create a folder if not exists"""
    full_path, path_dict = \
        Object.validate_full_path(full_path)
    folder_name = path_dict['filename']

    try:
        new_obj = Object.get_by_full_path(full_path, object_type='folder')
    except NotFoundError:
        # Create the folder
        if path_dict['path'] == '/':
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


def should_exclude(path, exclude_paths):
    if not exclude_paths:
        return False

    if path in exclude_paths:
        print("WARNING: Excluding path {}".format(path))
        return True

    for exclude_path in exclude_paths:
        if path.startswith(exclude_path):
            print("WARNING: Excluding path {}".format(path))
            return True

    return False


def _upload_folder(domain, vault, base_remote_path, base_local_path,
                   local_start, exclude_paths=None):

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
        _create_folder(vault, base_folder_path)

    # Create folders and upload files
    for abs_local_parent_path, folders, files in os.walk(base_local_path):

        # Strips off the local path and adds the parent directory at
        # each phase of the loop
        local_parent_path = re.sub(
            '^' + os.path.dirname(base_local_path), '', abs_local_parent_path
        ).lstrip('/')

        if should_exclude(abs_local_parent_path, exclude_paths):
            continue

        remote_folder_full_path = \
            os.path.join(base_remote_path, local_parent_path)

        # Create folders
        for folder in folders:
            new_folder_path = os.path.join(abs_local_parent_path, folder)
            if should_exclude(new_folder_path, exclude_paths):
                continue

            remote_path = os.path.join(remote_folder_full_path, folder)
            _create_folder(vault, remote_path)

        # Upload the files that do not yet exist on the remote
        for f in files:
            local_file_path = os.path.join(abs_local_parent_path, f)
            if should_exclude(local_file_path, exclude_paths):
                continue

            try:
                Object.get_by_full_path(
                    os.path.join(remote_folder_full_path, f))
            except NotFoundError:
                remote_parent = Object.get_by_full_path(
                    remote_folder_full_path, assert_type='folder')
                Object.upload_file(local_file_path, remote_parent.path,
                                   vault.full_path)


def create_dataset(args):
    """
    Attempt to create a new dataset given the following params:

        * template_id
        * template_file
        * capacity
        * create_vault
        * [argument] dataset name or full path

    NOTE: genome_build has been deprecated and is no longer used.

    """
    # For backwards compatibility, the "full_path" argument
    # can be a dataset filename, but only if vault and path
    # are set. If vault/path are both provided and there
    # are no forward-slashes in the "full_path", assume
    # the user has provided a dataset filename.
    if '/' not in args.full_path and args.vault and args.path:
        full_path, path_dict = Object.validate_full_path(
            '{0}:/{1}/{2}'.format(args.vault, args.path, args.full_path))
    else:
        full_path, path_dict = Object.validate_full_path(
            args.full_path, vault=args.vault, path=args.path)

    # Accept a template_id or a template_file
    if args.template_id:
        # Validate the template ID
        try:
            tpl = solvebio.DatasetTemplate.retrieve(args.template_id)
        except solvebio.SolveError as e:
            if e.status_code != 404:
                raise e
            print("No template with ID {0} found!"
                  .format(args.template_id))
            sys.exit(1)
    elif args.template_file:
        mode = 'r'
        fopen = open
        if check_gzip_path(args.template_file):
            mode = 'rb'
            fopen = gzip.open

        # Validate the template file
        with fopen(args.template_file, mode) as fp:
            try:
                tpl_json = json.load(fp)
            except:
                print('Template file {0} could not be loaded. Please '
                      'pass valid JSON'.format(args.template_file))
                sys.exit(1)

        tpl = solvebio.DatasetTemplate.create(**tpl_json)
        print("A new dataset template was created with id: {0}".format(tpl.id))
    else:
        print("Creating a new dataset {0} without a template."
              .format(full_path))
        tpl = None
        fields = []
        entity_type = None
        description = None

    if tpl:
        print("Creating new dataset {0} using the template '{1}'."
              .format(full_path, tpl.name))
        fields = tpl.fields
        entity_type = tpl.entity_type
        # include template used to create
        description = 'Created with dataset template: {0}'.format(str(tpl.id))

    return solvebio.Dataset.get_or_create_by_full_path(
        full_path,
        capacity=args.capacity,
        entity_type=entity_type,
        fields=fields,
        description=description,
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

            # Create the destination path (including subfolders) if not found
            parent_folder_path = vault.full_path + ':'
            folders = path_dict['path'].lstrip('/').split('/')
            for folder in folders:
                folder_full_path = os.path.join(parent_folder_path, folder)
                parent_folder = _create_folder(vault, folder_full_path)
                parent_folder_path = parent_folder.full_path

    exclude = args.exclude or []
    for local_path in args.local_path:
        local_path = local_path.rstrip('/')
        local_name = os.path.basename(local_path)

        if os.path.isdir(local_path):
            _upload_folder(path_dict['domain'], vault,
                           base_remote_path, local_path,
                           local_name, exclude_paths=exclude)
        else:
            # Upload if file does not exist
            try:
                full_path = os.path.join(path_dict['full_path'], local_name)
                Object.get_by_full_path(full_path)
                print("Notice: Object already exists: {}".format(full_path))
            except NotFoundError:
                Object.upload_file(local_path, path_dict['path'],
                                   vault.full_path)


def import_file(args):
    """
    Given a dataset and a local path, upload and import the file(s).

    Command arguments (args):

        * create_dataset
        * template_id
        * full_path
        * vault (optional, overrides the vault in full_path)
        * path (optional, overrides the path in full_path)
        * commit_mode
        * capacity
        * file (list)
        * follow (default: False)

    """
    full_path, path_dict = Object.validate_full_path(
        args.full_path, vault=args.vault, path=args.path)

    # Ensure the dataset exists. Create if necessary.
    if args.create_dataset:
        dataset = create_dataset(args)
    else:
        try:
            dataset = solvebio.Dataset.get_by_full_path(full_path)
        except solvebio.SolveError as e:
            if e.status_code != 404:
                raise e

            print("Dataset not found: {0}".format(full_path))
            print("Tip: use the --create-dataset flag "
                  "to create one from a template")
            sys.exit(1)

    # Generate a manifest from the local files
    manifest = solvebio.Manifest()
    manifest.add(*args.file)

    # Create the manifest-based import
    imp = solvebio.DatasetImport.create(
        dataset_id=dataset.id,
        manifest=manifest.manifest,
        commit_mode=args.commit_mode
    )

    if args.follow:
        imp.follow()
    else:
        mesh_url = 'https://my.solvebio.com/activity/'
        print("Your import has been submitted, view details at: {0}"
              .format(mesh_url))
