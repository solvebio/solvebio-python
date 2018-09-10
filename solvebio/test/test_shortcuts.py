from __future__ import absolute_import

import os
import json
import tempfile

import mock

from .helper import SolveBioTestCase

import solvebio
from solvebio.cli import main
from solvebio import DatasetTemplate
from solvebio.utils.files import get_home_dir
from solvebio.test.client_mocks import fake_vault_all
from solvebio.test.client_mocks import fake_vault_create
from solvebio.test.client_mocks import fake_object_all
from solvebio.test.client_mocks import fake_object_create
from solvebio.test.client_mocks import fake_dataset_create
from solvebio.test.client_mocks import fake_dataset_tmpl_create
from solvebio.test.client_mocks import fake_dataset_tmpl_retrieve
from solvebio.test.client_mocks import fake_dataset_import_create


def upload_path(*args, **kwargs):
    return '/'


class CLITests(SolveBioTestCase):
    def setUp(self):
        super(CLITests, self).setUp()
        # Set the global key for CLI tests only
        solvebio.api_key = os.environ.get('SOLVEBIO_API_KEY', None)

    @mock.patch('solvebio.resource.Vault.all')
    @mock.patch('solvebio.resource.Object.all')
    @mock.patch('solvebio.resource.Dataset.create')
    def test_create_dataset(self, DatasetCreate, ObjectAll, VaultAll):
        DatasetCreate.side_effect = fake_dataset_create
        ObjectAll.side_effect = fake_object_all
        VaultAll.side_effect = fake_vault_all
        args = ['create-dataset', 'solvebio:test_vault:/test-dataset',
                '--capacity', 'small']
        ds = main.main(args)
        self.assertEqual(ds.name, 'test-dataset')
        self.assertEqual(ds.path, '/test-dataset')

    @mock.patch('solvebio.resource.Vault.all')
    @mock.patch('solvebio.resource.Object.all')
    @mock.patch('solvebio.resource.Dataset.create')
    def test_create_dataset_by_filename(self, DatasetCreate, ObjectAll,
                                        VaultAll):
        DatasetCreate.side_effect = fake_dataset_create
        ObjectAll.side_effect = fake_object_all
        VaultAll.side_effect = fake_vault_all
        args = ['create-dataset', 'test-dataset-filename',
                '--vault', 'solvebio:test_vault',
                '--path', '/',
                '--capacity', 'small']
        ds = main.main(args)
        self.assertEqual(ds.name, 'test-dataset-filename')
        self.assertEqual(ds.path, '/test-dataset-filename')

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

    @mock.patch('solvebio.resource.Vault.all')
    @mock.patch('solvebio.resource.Object.all')
    @mock.patch('solvebio.resource.Dataset.create')
    @mock.patch('solvebio.resource.DatasetTemplate.create')
    def test_create_dataset_upload_template(self, TmplCreate,
                                            DatasetCreate, ObjectAll,
                                            VaultAll):
        TmplCreate.side_effect = fake_dataset_tmpl_create
        DatasetCreate.side_effect = fake_dataset_create
        ObjectAll.side_effect = fake_object_all
        VaultAll.side_effect = fake_vault_all

        template_path = os.path.join(os.path.dirname(__file__),
                                     "data/template.json")
        args = ['create-dataset', 'solvebio:test_vault:/test-dataset',
                   '--template-file', template_path,
                   '--capacity', 'medium']  # noqa

        ds = main.main(args)
        self.assertEqual(ds.description,
                         'Created with dataset template: 100')

    @mock.patch('solvebio.resource.Vault.all')
    @mock.patch('solvebio.resource.Object.all')
    @mock.patch('solvebio.resource.Dataset.create')
    @mock.patch('solvebio.resource.DatasetTemplate.retrieve')
    def test_create_dataset_template_id(self, TmplRetrieve, DatasetCreate,
                                        ObjectAll, VaultAll):
        VaultAll.side_effect = fake_vault_all
        ObjectAll.side_effect = fake_object_all
        DatasetCreate.side_effect = fake_dataset_create
        TmplRetrieve.side_effect = fake_dataset_tmpl_retrieve

        # create template
        template_path = os.path.join(os.path.dirname(__file__),
                                     "data/template.json")
        with open(template_path, 'r') as fp:
            tpl_json = json.load(fp)

        tpl = DatasetTemplate.create(**tpl_json)
        args = ['create-dataset', 'solvebio:test_vault:/test-dataset',
                   '--template-id', str(tpl.id),
                   '--capacity', 'small']  # noqa

        ds = main.main(args)
        self.assertEqual(ds.description,
                         'Created with dataset template: {0}'.format(tpl.id))

    @mock.patch('solvebio.resource.Vault.get_or_create_uploads_path')
    @mock.patch('solvebio.resource.Vault.get_by_full_path')
    @mock.patch('solvebio.resource.Vault.all')
    @mock.patch('solvebio.resource.Object.all')
    @mock.patch('solvebio.resource.Object.upload_file')
    @mock.patch('solvebio.resource.Dataset.create')
    @mock.patch('solvebio.resource.DatasetImport.create')
    def _test_import_file(self, args, DatasetImportCreate, DatasetCreate,
                          ObjectCreate, ObjectAll, VaultAll, VaultLookup,
                          UploadPath):
        DatasetImportCreate.side_effect = fake_dataset_import_create
        DatasetCreate.side_effect = fake_dataset_create
        ObjectAll.side_effect = fake_object_all
        ObjectCreate.side_effect = fake_object_create
        VaultAll.side_effect = fake_vault_all
        UploadPath.side_effect = upload_path
        VaultLookup.side_effect = fake_vault_create

        main.main(args)

    def test_import_file(self):
        _, file_ = tempfile.mkstemp(suffix='.txt')
        with open(file_, 'w') as fp:
            fp.write('blargh')

        args = ['import', '--create-dataset', '--follow',
                'solvebio:test_vault:/test-dataset', file_]

        self._test_import_file(args)

    def test_import_tilde(self):

        home = get_home_dir()

        _, file_ = tempfile.mkstemp(suffix='.txt')
        with open(file_, 'w') as fp:
            fp.write('blargh')

        for f in [
                '{0}:/test-dataset'.format(home),
                '{0}/test-dataset'.format(home),
        ]:
            args = ['import', '--create-dataset', '--follow', f, file_]
            self._test_import_file(args)
