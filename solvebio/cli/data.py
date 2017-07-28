# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function

import gzip
import json
import os
import re
import sys

import solvebio

from solvebio import Object, Vault
from solvebio.client import client
from solvebio.utils.files import check_gzip_path
from solvebio.errors import ObjectTypeError, NotFoundError


def create_dataset(args):
    """
    Attempt to create a new dataset given the following params:

        * dataset (full name)
        * template_id
        * template_file
        * capacity

    """
    if args.vault:
        vault_name = args.vault
    else:
        vault_name = Vault.get_personal_vault().name

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
              .format(args.dataset_name))
        tpl = None
        fields = []
        entity_type = None
        description = None

    if tpl:
        print("Creating new dataset {0} using the template '{1}'."
              .format(args.dataset_name, tpl.name))
        fields = tpl.fields
        entity_type = tpl.entity_type
        # include template used to create
        description = 'Created with dataset template: {0}'.format(str(tpl.id))

    return solvebio.Dataset.get_or_create_by_full_path(
        ':'.join([vault_name, os.path.join(args.path, args.dataset_name)]),
        capacity=args.capacity,
        entity_type=entity_type,
        fields=fields,
        description=description,
        create_vault=args.create_vault,
    )


def _make_full_path(s1, s2, s3):
    return ':'.join([s1, s2, s3])


def _assert_object_type(obj, object_type):
    if obj.object_type != object_type:
        raise ObjectTypeError('{0} is a {1} but must be a folder'.format(
            obj.path,
            obj.object_type,
        ))


def upload(args):
    """
    Given a folder or file, upload all the folders and files contained
    within it, skipping ones that already exist on the remote.
    """
    if args.vault:
        vault_name = args.vault
    else:
        vault_name = Vault.get_personal_vault().name

    # '--path /remote/path1 local/path2'
    # base_remote_path = /remote/path1
    # base_local_path = local/path2
    # local_shart = 'path2'
    base_remote_path = args.path
    base_local_paths = args.local_path

    user = client.get('/v1/user', {})
    domain = user['account']['domain']

    vaults = Vault.all(name=vault_name)

    if len(vaults.data) == 0:
        raise Exception('Vault not found with name "{0}"'.format(vault_name))
    else:
        vault = vaults.data[0]

    for local_path in base_local_paths:

        local_path = local_path.rstrip('/')
        local_start = os.path.basename(local_path)

        if os.path.isdir(local_path):
            _upload_folder(domain, vault, base_remote_path,
                           local_path, local_start)
        else:
            if base_remote_path != '/':
                base_full_remote_path = _make_full_path(
                    domain,
                    vault.name,
                    base_remote_path,
                )
                base_remote_object = Object.get_by_full_path(
                    base_full_remote_path)
                _assert_object_type(base_remote_object, 'folder')
                base_remote_path = base_remote_object.path
            else:
                base_remote_path = '/'

            Object.upload_file(local_path, base_remote_path,
                               vault.name)


def _upload_folder(domain, vault, base_remote_path, base_local_path,
                   local_start):
    # Create the root folder if it does not exist on the remote
    try:
        full_root_path = _make_full_path(
            domain,
            vault.name,
            os.path.join(base_remote_path, local_start),
        )
        root_object = Object.get_by_full_path(full_root_path)
        _assert_object_type(root_object, 'folder')
    except NotFoundError:
        if base_remote_path == '/':
            parent_object_id = None
        else:
            base_remote_full_path = _make_full_path(
                domain,
                vault.name,
                base_remote_path,
            )
            obj = Object.get_by_full_path(base_remote_full_path)
            _assert_object_type(obj, 'folder')
            parent_object_id = obj.id

        new_folder = Object.create(
            vault_id=vault.id,
            parent_object_id=parent_object_id,
            object_type='folder',
            filename=local_start,
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
            full_path = _make_full_path(domain, vault.name, dirpath)

            try:
                Object.get_by_full_path(full_path, object_type='folder')
            except NotFoundError:
                # Create the folder
                if os.path.dirname(dirpath) == '/':
                    parent_object_id = None
                else:
                    parent_full_path = _make_full_path(
                        domain, vault.name,
                        os.path.dirname(dirpath))

                    parent = Object.get_by_full_path(parent_full_path)
                    _assert_object_type(parent, 'folder')
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
            file_full_path = _make_full_path(
                domain,
                vault.name,
                os.path.join(
                    base_remote_path,
                    re.sub('^' + os.path.dirname(base_local_path),
                           '',
                           root).lstrip('/'),
                    f,
                )
            )
            try:
                Object.get_by_full_path(file_full_path)
            except NotFoundError:
                parent_full_path = _make_full_path(
                    domain,
                    vault.name,
                    os.path.dirname(
                        os.path.join(
                            base_remote_path,
                            re.sub('^' + os.path.dirname(base_local_path),
                                   '',
                                   root).lstrip('/'),
                            f,
                        )
                    )
                )
                parent = Object.get_by_full_path(parent_full_path)
                _assert_object_type(parent, 'folder')
                Object.upload_file(os.path.join(root, f), parent.path,
                                   vault.name)


def import_file(args):
    """
    Given a dataset and a local path, upload and import the file(s).

    Command arguments (args):

        * create_dataset
        * template_id
        * vault_name
        * path
        * follow (default: False)
        * dataset
        * capacity
        * file (list)

    """
    if not solvebio.api_key:
        solvebio.login()

    if args.vault:
        vault_name = args.vault
    else:
        vault_name = Vault.get_personal_vault().name

    # Ensure the dataset exists. Create if necessary.
    if args.create_dataset:
        dataset = create_dataset(args)
    else:
        try:
            full_path = solvebio.Dataset.make_full_path(vault_name,
                                                        args.path,
                                                        args.dataset_name)
            dataset = solvebio.Dataset.get_by_full_path(full_path)
        except solvebio.SolveError as e:
            if e.status_code != 404:
                raise e

            print("Dataset not found: {0}".format(args.dataset_name))
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
        mesh_url = 'https://my.solvebio.com/jobs/imports/{0}'.format(imp.id)
        print("Your import has been submitted, view details at: {0}"
              .format(mesh_url))
