from __future__ import absolute_import

import os
import json
import tempfile

import mock

from .helper import SolveBioTestCase

import solvebio
from solvebio.cli import main
from solvebio import DatasetTemplate
from solvebio import Vault
from solvebio.errors import NotFoundError
from solvebio.utils.files import get_home_dir
from solvebio.cli.data import _create_folder
from solvebio.cli.data import should_exclude
from solvebio.test.client_mocks import fake_vault_all
from solvebio.test.client_mocks import fake_vault_create
from solvebio.test.client_mocks import fake_object_all
from solvebio.test.client_mocks import fake_object_create
from solvebio.test.client_mocks import fake_object_retrieve
from solvebio.test.client_mocks import fake_dataset_create
from solvebio.test.client_mocks import fake_dataset_tmpl_create
from solvebio.test.client_mocks import fake_dataset_tmpl_retrieve
from solvebio.test.client_mocks import fake_dataset_import_create


def raise_not_found(*args, **kwargs):
    raise NotFoundError


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
    @mock.patch('solvebio.resource.DatasetTemplate.create')
    def test_create_dataset_template_id(self, TmplCreate, TmplRetrieve,
                                        DatasetCreate, ObjectAll, VaultAll):
        VaultAll.side_effect = fake_vault_all
        ObjectAll.side_effect = fake_object_all
        DatasetCreate.side_effect = fake_dataset_create
        TmplRetrieve.side_effect = fake_dataset_tmpl_retrieve
        TmplCreate.side_effect = fake_dataset_tmpl_create

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

    @mock.patch(
        'solvebio.resource.apiresource.ListableAPIResource._retrieve_helper')
    @mock.patch('solvebio.resource.Vault.get_by_full_path')
    @mock.patch('solvebio.resource.Vault.all')
    @mock.patch('solvebio.resource.Object.all')
    @mock.patch('solvebio.resource.Object.create')
    @mock.patch('solvebio.resource.Object.upload_file')
    def _test_upload_command(self, args, ObjectUpload, ObjectCreate,
                             ObjectAll, VaultAll, VaultLookup, RetrieveHelper,
                             **kwargs):

        ObjectUpload.side_effect = fake_object_create
        ObjectAll.side_effect = fake_object_all
        ObjectCreate.side_effect = fake_object_create
        VaultAll.side_effect = fake_vault_all
        VaultLookup.side_effect = fake_vault_create

        if 'fail_lookup' in kwargs:
            RetrieveHelper.side_effect = raise_not_found
        else:
            RetrieveHelper.side_effect = fake_object_retrieve

        main.main(args)

    def test_upload_file(self):
        _, file_ = tempfile.mkstemp(suffix='.txt')
        with open(file_, 'w') as fp:
            fp.write('blargh')

        args = ['upload', '--full-path',
                'solvebio:test_vault:/test-folder', file_]
        with self.assertRaises(NotFoundError):
            self._test_upload_command(args, fail_lookup=True)

        # pass -p to create destination
        args = ['upload', '--full-path',
                'solvebio:test_vault:/test-folder',
                '--create-full-path', file_]
        self._test_upload_command(args)

    def test_upload_directories(self):
        folder_ = tempfile.mkdtemp(suffix='.txt')
        inner_folder_ = tempfile.mkdtemp(suffix='.txt', dir=folder_)
        _, file_ = tempfile.mkstemp(suffix='.txt', dir=inner_folder_)
        with open(file_, 'w') as fp:
            fp.write('blargh')

        args = ['upload', '--full-path',
                'solvebio:test_vault:/test-folder-upload', folder_]
        with self.assertRaises(NotFoundError):
            self._test_upload_command(args, fail_lookup=True)

        # pass -p to create destination
        args = ['upload', '--full-path',
                'solvebio:test_vault:/test-folder-upload',
                '--create-full-path', folder_]
        self._test_upload_command(args)

    @mock.patch(
        'solvebio.resource.apiresource.ListableAPIResource._retrieve_helper')
    @mock.patch('solvebio.resource.Object.all')
    @mock.patch('solvebio.resource.Object.create')
    @mock.patch('solvebio.resource.Vault.create')
    def test_create_folder(self, VaultCreate, ObjectCreate, ObjectAll,
                           RetrieveHelper):

        VaultCreate.side_effect = fake_vault_create
        ObjectAll.side_effect = fake_object_all
        ObjectCreate.side_effect = fake_object_create

        vault = Vault.create('my-vault')

        # create folder

        RetrieveHelper.side_effect = fake_object_retrieve
        full_path = vault.full_path + ':/new_folder'
        f = _create_folder(vault, full_path)
        self.assertEqual(f.full_path, full_path)

    def test_should_exclude(self):
        exclude = ['~/test', '~/test2']
        self.assertFalse(should_exclude('~/test3/file.txt', exclude))

        exclude = ['~/test*']
        self.assertTrue(should_exclude('~/test3/file.txt', exclude))

        exclude = ['*file.txt']
        self.assertTrue(should_exclude('~/test3/file.txt', exclude))

        exclude = ['*file.json']
        self.assertFalse(should_exclude('~/test3/file.txt', exclude))

        exclude = ['~/']
        self.assertTrue(should_exclude('~/test3/file.txt', exclude))

        exclude = ['~/test3/']
        self.assertTrue(should_exclude('~/test3/file.txt', exclude))

        exclude = ['~/test3']
        self.assertTrue(should_exclude('~/test3/file.txt', exclude))

        exclude = ['~/*']
        self.assertTrue(should_exclude('~/test3/file.txt', exclude))

        exclude = ['~/test3/*']
        self.assertTrue(should_exclude('~/test3/file.txt', exclude))

        exclude = ['file.txt']
        self.assertFalse(should_exclude('~/test3/file.txt', exclude))

        exclude = ['~/test3/file.txt']
        self.assertTrue(should_exclude('~/test3/file.txt', exclude))

        exclude = ['*file.txt']
        self.assertTrue(should_exclude('~/test3/file.txt', exclude))

        exclude = ['*/folder/*/file.txt']
        self.assertTrue(should_exclude('~/folder/2019-01-01/file.txt',
                                       exclude))

        exclude = ['*/folder/*/new/file.txt']
        self.assertFalse(should_exclude('~/folder/2019-01-01/file.txt',
                                        exclude))

        exclude = ['folder']
        self.assertFalse(should_exclude('~/folder/2019-01-01/file.txt',
                                        exclude))

        exclude = ['*folder']
        self.assertTrue(should_exclude('~/folder/2019-01-01/file.txt',
                                        exclude))

        exclude = ['*folder*']
        self.assertTrue(should_exclude('~/folder/2019-01-01/file.txt',
                                        exclude))
