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

    """
    tpl_fields = []
    is_genomic = args.genome_build is not None
    entity_type = None

    # Accept a template_id or a template_file
    if args.template_id or args.template_file:
        tpl = None
        if args.template_id:
            # Validate the template ID
            try:
                tpl = solvebio.DatasetTemplate.retrieve(args.template_id)
            except solvebio.SolveError as e:
                if e.status_code != 404:
                    raise e
                print("No template with ID {0} found!"
                      .format(args.template_id))
        elif args.template_file:
            fopen = gzip.open if check_gzip_path(args.template_file) else open
            # Validate the template file
            with fopen(args.template_file, 'rb') as fp:
                try:
                    template_contents = json.load(fp)
                except:
                    print('Template file {0} could not be loaded. Please '
                          'pass valid JSON'.format(args.template_file))
                    sys.exit(1)

            # assign ownership to the template
            user = solvebio.User.retrieve()
            template_contents['user'] = user.id

            try:
                tpl = solvebio.DatasetTemplate.create(**template_contents)
            except solvebio.SolveError as e:
                if e.status_code != 404:
                    raise e
                print("Template could not be created!")
        else:
            print("Cannot create a new dataset: "
                  "must specify a template ID with the --template-id flag.")

        if not tpl:
            print("Choose an ID from one of the following templates: ")
            print(solvebio.DatasetTemplate.all())
            sys.exit(1)

        # Template is valid.
        print("Creating new dataset {0} using the template '{1}'."
              .format(args.dataset, tpl.name))

        # get fields from template
        tpl_fields = tpl.fields
        is_genomic = tpl.is_genomic
        entity_type = tpl.entity_type

    genome_builds = [args.genome_build] if args.genome_build else None
    return solvebio.Dataset.get_or_create_by_full_name(
        full_name=args.dataset,
        genome_builds=genome_builds,
        is_genomic=is_genomic,
        entity_type=entity_type,
        fields=tpl_fields)


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
        * file (list)

    """
    if not solvebio.api_key:
        solvebio.login()

    # Ensure the dataset exists. Create if necessary.
    try:
        dataset = solvebio.Dataset.retrieve(args.dataset)
    except solvebio.SolveError as e:
        if e.status_code != 404:
            raise e

        print("Dataset not found: {0}".format(args.dataset))

        if args.create_dataset:
            dataset = create_dataset(args)
        else:
            print("Tip: use the --create-dataset flag "
                  "to create one automatically")
            sys.exit(1)

    # Generate a manifest from the local files
    manifest = solvebio.Manifest()
    manifest.add(*args.file)

    # Create the manifest-based import
    imp = solvebio.DatasetImport.create(
        dataset_id=dataset.id,
        manifest=manifest.manifest,
        genome_build=args.genome_build,
        auto_approve=args.auto_approve)

    if args.follow:
        imp.follow()
    else:
        mesh_url = 'https://my.solvebio.com/jobs/imports/{0}'.format(imp.id)
        print("Your import has been submitted, view details at: {0}"
              .format(mesh_url))
