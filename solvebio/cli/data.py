# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function

import gzip
import json
import os
import re
import sys

import solvebio

from solvebio import Vault
from solvebio import Object
from solvebio.utils.files import check_gzip_path
from solvebio.errors import NotFoundError


def _upload_folder(domain, vault, base_remote_path,
                   base_local_path, local_start):

    # Create the upload root folder if it does not exist on the remote
    try:
        upload_root_path, _ = Object.validate_full_path(
            os.path.join(base_remote_path, local_start)
        )
        obj = Object.get_by_full_path(upload_root_path, assert_type='folder')
    except NotFoundError:
        base_remote_path, path_dict = \
            Object.validate_full_path(base_remote_path)

        if path_dict['path'] == '/':
            parent_object_id = None
        else:
            obj = Object.get_by_full_path(base_remote_path,
                                          assert_type='folder')
            parent_object_id = obj.id

        # Create base folder
        new_folder = Object.create(
            vault_id=vault.id,
            parent_object_id=parent_object_id,
            object_type='folder',
            filename=local_start
        )

        print('Notice: Folder created for {0} at {1}'.format(
            base_local_path,
            new_folder.path,
        ))

    for root, dirs, files in os.walk(base_local_path):

        # Create the sub-folders that do not exist on the remote
        for d in dirs:
            dirpath = os.path.join(
                base_remote_path,
                re.sub('^' + os.path.dirname(base_local_path), '', root).lstrip('/'),  # noqa
                d
            )

            try:
                Object.get_by_full_path(dirpath, object_type='folder')
            except NotFoundError:
                # Create the folder
                if os.path.dirname(dirpath.split(':')[-1]) == '/':
                    parent_object_id = None
                else:
                    parent_full_path = os.path.dirname(dirpath)
                    parent = Object.get_by_full_path(
                        parent_full_path, assert_type='folder')
                    parent_object_id = parent.id

                # Make the API call
                new_obj = Object.create(
                    vault_id=vault.id,
                    parent_object_id=parent_object_id,
                    object_type='folder',
                    filename=d,
                )

                print('Notice: Folder created for {0} at {1}'
                      .format(os.path.join(root, d), new_obj.path))

        # Upload the files that do not yet exist on the remote
        for f in files:
            file_full_path = os.path.join(
                base_remote_path,
                re.sub('^' + os.path.dirname(base_local_path),
                       '',
                       root).lstrip('/'),
                f,
            )
            try:
                Object.get_by_full_path(file_full_path)
            except NotFoundError:
                parent_full_path = os.path.dirname(
                    os.path.join(
                        base_remote_path,
                        re.sub('^' + os.path.dirname(base_local_path),
                               '',
                               root).lstrip('/'),
                        f,
                    )
                )
                parent = Object.get_by_full_path(
                    parent_full_path, assert_type='folder')
                Object.upload_file(os.path.join(root, f),
                                   parent.path, vault.full_path)


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
    base_remote_path, path_dict = Object.validate_full_path(
        args.full_path, vault=args.vault, path=args.path)

    # Assert the vault exists and is accessible
    vault = Vault.get_by_full_path(path_dict['vault_full_path'])

    # If not the vault root, validate remote path exists and is a folder
    if path_dict['path'] != '/':
        Object.get_by_full_path(base_remote_path, assert_type='folder')

    for local_path in args.local_path:
        local_path = local_path.rstrip('/')
        local_start = os.path.basename(local_path)

        if os.path.isdir(local_path):
            _upload_folder(path_dict['domain'], vault,
                           base_remote_path, local_path, local_start)
        else:
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
