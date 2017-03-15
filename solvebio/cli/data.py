# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function

import sys
import gzip
import json

import solvebio

from solvebio.utils.files import check_gzip_path


def create_dataset(args):
    """
    Attempt to create a new dataset given the following params:

        * dataset (full name)
        * template_id
        * template_file
        * genome_build
        * capacity

    """
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
              .format(args.dataset))
        tpl = None
        fields = []
        entity_type = None
        is_genomic = bool(args.genome_build)
        description = None

    if tpl:
        print("Creating new dataset {0} using the template '{1}'."
              .format(args.dataset, tpl.name))
        fields = tpl.fields
        entity_type = tpl.entity_type
        is_genomic = bool(args.genome_build) or tpl.is_genomic
        # include template used to create
        description = 'Created with dataset template: {0}'.format(str(tpl.id))

    genome_builds = [args.genome_build] if is_genomic else None
    return solvebio.Dataset.get_or_create_by_full_name(
        full_name=args.dataset,
        is_genomic=is_genomic,
        genome_builds=genome_builds,
        capacity=args.capacity,
        entity_type=entity_type,
        fields=fields,
        description=description
    )


def import_file(args):
    """
    Given a dataset and a local path, upload and import the file(s).

    Command arguments (args):

        * create_dataset
        * template_id
        * genome_build
        * follow (default: False)
        * auto_approve (default: False)
        * dataset
        * capacity
        * file (list)

    """
    if not solvebio.api_key:
        solvebio.login()

    # Ensure the dataset exists. Create if necessary.
    if args.create_dataset:
        dataset = create_dataset(args)
    else:
        try:
            dataset = solvebio.Dataset.retrieve(args.dataset)
        except solvebio.SolveError as e:
            if e.status_code != 404:
                raise e

            print("Dataset not found: {0}".format(args.dataset))
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
        genome_build=args.genome_build,
        commit_mode=args.commit_mode,
        auto_approve=args.auto_approve)

    if args.follow:
        imp.follow()
    else:
        mesh_url = 'https://my.solvebio.com/jobs/imports/{0}'.format(imp.id)
        print("Your import has been submitted, view details at: {0}"
              .format(mesh_url))
