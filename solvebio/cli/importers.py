# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function

import sys
import time

import solvebio


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
            if args.template_id:
                # Validate the template ID
                try:
                    tpl = solvebio.DatasetTemplate.retrieve(args.template_id)
                except solvebio.SolveError as e:
                    if e.status_code != 404:
                        raise e
                    tpl = None
                    print("No template with ID {0} found!"
                          .format(args.template_id))
            else:
                tpl = None
                print("Cannot create a new dataset: "
                      "no template ID specified by the --template-id flag!")

            if not tpl:
                print("Choose an ID from one of the following templates: ")
                print(solvebio.DatasetTemplate.all())
                sys.exit(1)

            # Template is valid.
            print("Creating new dataset {0} using the template '{1}'."
                  .format(args.dataset, tpl.name))

            genome_builds = [args.genome_build] if args.genome_build else None
            dataset = solvebio.Dataset.get_or_create_from_full_name(
                full_name=args.dataset,
                genome_builds=genome_builds,
                is_genomic=tpl.is_genomic,
                entity_type=tpl.entity_type,
                fields=tpl.fields)
        else:
            print("Tip: use the --create-dataset flag "
                  "to create one automatically")
            sys.exit(1)

    # Upload and import the file(s)
    for path in args.file:
        print("Uploading file: {0}".format(path))
        upload = solvebio.Upload.create(path=path)
        print("Upload complete (id = {0})".format(upload.id))
        print("Creating new import for dataset: {0}".format(dataset.full_name))
        imp = solvebio.DatasetImport.create(
            dataset_id=dataset.id,
            upload_id=upload.id,
            genome_build=args.genome_build,
            auto_approve=args.auto_approve)

        if args.follow:
            print("Waiting for import (id = {0}) to start...".format(imp.id))
            print("View your import status on MESH: "
                  "https://my.solvebio.com/jobs/imports/{0}"
                  .format(imp.id))

            status, records, polls = imp.status, None, 0
            while imp.status in ['queued', 'running']:
                if imp.status == 'running':
                    if polls == 0:
                        # Just print this once, the first time we see "running"
                        print("Processing and validating uploaded file...")
                    elif imp.dataset_commits:
                        commit = imp.dataset_commits[0]
                        if not commit.is_approved:
                            print("Dataset commit (id = {0}) is now "
                                  "awaiting admin approval".format(commit.id))
                            print("Visit the following URL to approve it: "
                                  "https://my.solvebio.com/jobs/imports/{0}"
                                  .format(imp.id))
                            # Nothing we can do here!
                            break

                        if records is None or \
                                commit.records_modified > records:
                            percent = float(commit.records_modified) / \
                                float(commit.records_total) * 100.00
                            print("Imported {0}/{1} ({2}%) records".format(
                                commit.records_modified, commit.records_total,
                                int(percent)))
                        records = commit.records_modified

                time.sleep(2)
                imp.refresh()
                polls += 1
                if imp.status != status:
                    print("Import is now {0} (was {1})"
                          .format(imp.status, status))
                    status = imp.status
                    polls = 0

            if imp.status == 'completed':
                print("\nImport completed!")
                print("View your imported data: "
                      "https://my.solvebio.com/data/{0}"
                      .format(dataset.full_name))

    return True
