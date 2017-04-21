from __future__ import absolute_import

import os
import time
import json
import random

from solvebio.cli import main
from .helper import SolveBioTestCase
from solvebio import User
from solvebio import Depository
from solvebio import DatasetTemplate


class CLITests(SolveBioTestCase):

    def test_whoami(self):
        email, token = main.main(['whoami'])
        self.assertEqual(token, os.environ.get('SOLVEBIO_API_KEY'))

    def unique_dataset_name(self):
        user = User.retrieve()
        domain = user['account']['domain']
        return  \
            '{0}:test-client-{1}-{2}/1.0.0/test-{1}-{2}'.format(
                domain, int(time.time()), random.randint(0, 100000))

    def test_create_dataset(self):
        # TODO mock client responses or allow for hard
        # cleanup of dataset/depo
        dataset_full_name = self.unique_dataset_name()

        args = ['create-dataset', dataset_full_name,
                   '--capacity', 'small']  # noqa
        ds = main.main(args)
        self.assertEqual(ds.full_name, dataset_full_name)

        # does soft delete of depo
        depo = Depository.retrieve(ds.depository_id)
        depo.delete()

    def _validate_tmpl_fields(self, fields):
        for f in fields:
            if f.name == 'name':
                self.assertEqual(f.entity_type, 'gene')
            elif f.name == 'variants':
                self.assertEqual(f.entity_type, 'variant')
                self.assertEqual(f.is_list, True)
                self.assertEqual(f.data_type, 'auto')
            elif f.name == 'aliases':
                self.assertEqual(f.data_type, 'string')

    def test_create_dataset_upload_template(self):
        # TODO mock client responses or allow for hard
        # cleanup of template and dataset/depo
        dataset_full_name = self.unique_dataset_name()
        template_path = os.path.join(os.path.dirname(__file__),
                                     "data/template.json")
        args = ['create-dataset', dataset_full_name,
                   '--template-file', template_path,
                   '--capacity', 'medium']  # noqa
        ds = main.main(args)
        self.assertEqual(ds.full_name, dataset_full_name)

        # validate fields
        self._validate_tmpl_fields(ds.fields())

        # does hard delete of template
        id_prefix = 'Created with dataset template: '
        if not ds.description.startswith(id_prefix):
            raise Exception("Dataset with template ID not found.")

        template_id = ds.description.replace(id_prefix, '')
        tpl = DatasetTemplate.retrieve(template_id)
        tpl.delete()

        # does soft delete of depo
        depo = Depository.retrieve(ds.depository_id)
        depo.delete()

    def test_create_dataset_template_id(self):
        # TODO mock client responses or allow for hard
        # cleanup of template and dataset/depo
        dataset_full_name = self.unique_dataset_name()

        # create template
        template_path = os.path.join(os.path.dirname(__file__),
                                     "data/template.json")
        with open(template_path, 'r') as fp:
            tpl_json = json.load(fp)

        tpl = DatasetTemplate.create(**tpl_json)
        args = ['create-dataset', dataset_full_name,
                   '--template-id', str(tpl.id),
                   '--capacity', 'large']  # noqa
        ds = main.main(args)
        self.assertEqual(ds.full_name, dataset_full_name)

        # validate fields
        self._validate_tmpl_fields(ds.fields())

        # cleanup
        tpl.delete()

        # does soft delete of depo
        depo = Depository.retrieve(ds.depository_id)
        depo.delete()
