from __future__ import absolute_import

import os
import time
import json
import random

import mock

from solvebio.cli import main
from .helper import SolveBioTestCase
from solvebio import User
from solvebio import DatasetTemplate
from solvebio.test.client_mocks import fake_vault_create
from solvebio.test.client_mocks import fake_vault_all
from solvebio.test.client_mocks import fake_object_all
from solvebio.test.client_mocks import fake_dataset_create
from solvebio.test.client_mocks import fake_data_tpl_create
from solvebio.test.client_mocks import fake_data_tpl_retrieve


class CLITests(SolveBioTestCase):

    def test_whoami(self):
        email, token = main.main(['whoami'])
        self.assertEqual(token, os.environ.get('SOLVEBIO_API_KEY'))

    @mock.patch('solvebio.resource.Vault.all',
                side_effect=fake_vault_all)
    @mock.patch('solvebio.resource.Object.all',
                side_effect=fake_object_all)
    @mock.patch('solvebio.resource.Dataset.create',
                side_effect=fake_dataset_create)
    def test_create_dataset(self,
                            fake_vault_all,
                            fake_object_all,
                            fake_dataset_create):
        args = ['create-dataset', 'test-dataset',
                   '--capacity', 'small',
                   '--vault', 'test',
                   '--path', '/']  # noqa
        ds = main.main(args)
        self.assertEqual(ds.name, 'test-dataset')
        self.assertEqual(ds.path, '/test-dataset')

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

    @mock.patch('solvebio.resource.Vault.all',
                side_effect=fake_vault_all)
    @mock.patch('solvebio.resource.Object.all',
                side_effect=fake_object_all)
    @mock.patch('solvebio.resource.Dataset.create',
                side_effect=fake_dataset_create)
    @mock.patch('solvebio.resource.DatasetTemplate.create',
                side_effect=fake_data_tpl_create)
    def test_create_dataset_upload_template(
            self,
            fake_vault_all,
            fake_object_all,
            fake_dataset_create,
            fake_data_tpl_create):
        template_path = os.path.join(os.path.dirname(__file__),
                                     "data/template.json")
        args = ['create-dataset', 'test-dataset',
                   '--template-file', template_path,
                   '--capacity', 'medium',
                   '--vault', 'test',
                   '--path', '/']  # noqa

        ds = main.main(args)
        self.assertEqual(ds.description,
                         'Created with dataset template: 100')

    @mock.patch('solvebio.resource.DatasetTemplate.retrieve',
                side_effect=fake_data_tpl_retrieve)
    @mock.patch('solvebio.resource.Vault.all',
                side_effect=fake_vault_all)
    @mock.patch('solvebio.resource.Object.all',
                side_effect=fake_object_all)
    @mock.patch('solvebio.resource.Dataset.create',
                side_effect=fake_dataset_create)
    def test_create_dataset_template_id(
            self,
            fake_data_tpl_retrieve,
            fake_vault_all,
            fake_object_all,
            fake_dataset_create):

        # create template
        template_path = os.path.join(os.path.dirname(__file__),
                                     "data/template.json")
        with open(template_path, 'r') as fp:
            tpl_json = json.load(fp)

        tpl = DatasetTemplate.create(**tpl_json)
        args = ['create-dataset', 'test-dataset',
                   '--template-id', str(tpl.id),
                   '--capacity', 'small',
                   '--vault', 'test',
                   '--path', '/']  # noqa

        ds = main.main(args)
        self.assertEqual(ds.description,
                         'Created with dataset template: {0}'.format(tpl.id))
