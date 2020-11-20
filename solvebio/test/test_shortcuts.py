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
from solvebio.cli.data import _create_folder
from solvebio.cli.data import should_exclude
from solvebio.test.client_mocks import fake_vault_all
from solvebio.test.client_mocks import fake_vault_create
from solvebio.test.client_mocks import fake_object_all
from solvebio.test.client_mocks import fake_object_create
from solvebio.test.client_mocks import fake_object_retrieve
from solvebio.test.client_mocks import fake_dataset_tmpl_create
from solvebio.test.client_mocks import fake_dataset_tmpl_retrieve
from solvebio.test.client_mocks import fake_dataset_import_create
from solvebio.test.client_mocks import fake_dataset_get_or_create


def raise_not_found(*args, **kwargs):
    raise NotFoundError


def upload_path(*args, **kwargs):
    return '/'


class CLITests(SolveBioTestCase):
    def setUp(self):
        super(CLITests, self).setUp()
        # Set the global key for CLI tests only
        solvebio.api_key = os.environ.get('SOLVEBIO_API_KEY', None)
        solvebio.api_host = os.environ.get('SOLVEBIO_API_HOST', None)


class CreateDatasetTests(CLITests):

    @mock.patch('solvebio.resource.Vault.all')
    @mock.patch('solvebio.resource.Object.all')
    @mock.patch('solvebio.resource.Dataset.get_or_create_by_full_path')
    @mock.patch('solvebio.resource.DatasetTemplate.create')
    @mock.patch('solvebio.resource.DatasetTemplate.retrieve')
    def _test_create_dataset(self, args, TmplRetrieve, TmplCreate,
                             DatasetCreate, ObjectAll, VaultAll):
        TmplRetrieve.side_effect = fake_dataset_tmpl_retrieve
        TmplCreate.side_effect = fake_dataset_tmpl_create
        DatasetCreate.side_effect = fake_dataset_get_or_create
        ObjectAll.side_effect = fake_object_all
        VaultAll.side_effect = fake_vault_all
        return main.main(args)

    def test_create_dataset(self):
        args = ['create-dataset', 'solvebio:test_vault:/test-dataset',
                '--capacity', 'small']
        ds = self._test_create_dataset(args)
        self.assertEqual(ds.filename, 'test-dataset')
        self.assertEqual(ds.path, '/test-dataset')

    def test_create_dataset_by_filename(self):
        args = [
            'create-dataset',
            'solvebio:test_vault:/test-dataset-filename',
            '--capacity', 'small',
            '--tag', 'tag_test',
            '--metadata', 'TEST=tag',
            '--metadata', 'TEST2=tag2',
        ]
        ds = self._test_create_dataset(args)
        self.assertEqual(ds.filename, 'test-dataset-filename')
        self.assertEqual(ds.path, '/test-dataset-filename')
        self.assertEqual(ds.capacity, 'small')
        self.assertEqual(ds.tags, ['tag_test'])
        self.assertEqual(ds.metadata, dict(TEST='tag', TEST2='tag2'))

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
        template_path = os.path.join(os.path.dirname(__file__),
                                     "data/template.json")
        args = ['create-dataset', 'solvebio:test_vault:/test-dataset',
                   '--template-file', template_path,
                   '--capacity', 'medium']  # noqa

        ds = self._test_create_dataset(args)
        self.assertEqual(ds.description,
                         'Created with dataset template: 100')

    @mock.patch('solvebio.resource.DatasetTemplate.create')
    def test_create_dataset_template_id(self, TmplCreate):
        # create template
        template_path = os.path.join(os.path.dirname(__file__),
                                     "data/template.json")
        with open(template_path, 'r') as fp:
            tpl_json = json.load(fp)

        TmplCreate.side_effect = fake_dataset_tmpl_create
        tpl = DatasetTemplate.create(**tpl_json)
        args = ['create-dataset', 'solvebio:test_vault:/test-dataset',
                   '--template-id', str(tpl.id),
                   '--capacity', 'small']  # noqa

        ds = self._test_create_dataset(args)
        self.assertEqual(ds.description,
                         'Created with dataset template: {0}'.format(tpl.id))


class ImportTests(CLITests):
    @mock.patch('solvebio.resource.DatasetTemplate.retrieve')
    @mock.patch('solvebio.resource.DatasetTemplate.create')
    @mock.patch('solvebio.resource.Vault.get_or_create_uploads_path')
    @mock.patch('solvebio.resource.Vault.get_by_full_path')
    @mock.patch('solvebio.resource.Vault.all')
    @mock.patch('solvebio.resource.Object.all')
    @mock.patch('solvebio.resource.Object.upload_file')
    @mock.patch('solvebio.resource.Object.create')
    @mock.patch('solvebio.resource.DatasetImport.create')
    @mock.patch('solvebio.resource.Dataset.get_or_create_by_full_path')
    def _test_import_file(self, args, DatasetGetCreate, DatasetImportCreate,
                          ObjectCreate, UploadFile, ObjectAll, VaultAll,
                          VaultLookup, UploadPath, TmplCreate, TmplRetrieve):
        DatasetGetCreate.side_effect = fake_dataset_get_or_create
        DatasetImportCreate.side_effect = fake_dataset_import_create
        ObjectCreate.side_effect = fake_object_create
        UploadFile.side_effect = fake_object_create
        ObjectAll.side_effect = fake_object_all
        VaultAll.side_effect = fake_vault_all
        UploadPath.side_effect = upload_path
        VaultLookup.side_effect = fake_vault_create
        TmplRetrieve.side_effect = fake_dataset_tmpl_retrieve
        TmplCreate.side_effect = fake_dataset_tmpl_create

        # returns (imports_list, dataset)
        return main.main(args)

    def test_import_file(self):
        _, file_ = tempfile.mkstemp(suffix='.txt')
        with open(file_, 'w') as fp:
            fp.write('blargh')

        args = ['import', '--create-dataset', '--tag', 'hello', '--follow',
                '--commit-mode', 'overwrite',
                'solvebio:mock_vault:/test-dataset', file_]

        imports, ds = self._test_import_file(args)
        self.assertEqual(ds.full_path, 'solvebio:mock_vault:/test-dataset')
        self.assertEqual(ds.tags, ['hello'])

        # should be a manifest with a single file
        self.assertEqual(len(imports[0].manifest['files']), 1)
        self.assertEqual(imports[0]['commit_mode'], 'overwrite')

        # Non-existent file
        args = ['import', '--create-dataset', '--tag', 'hello', '--follow',
                'solvebio:mock_vault:/test-dataset',
                'not/a/real/path/file.txt']

        with self.assertRaises(ValueError):
            self._test_import_file(args)

    def test_import_tilde(self):
        _, file_ = tempfile.mkstemp(suffix='.txt')
        with open(file_, 'w') as fp:
            fp.write('blargh')

        for dataset_path in [
                '~/test-dataset',
                '~:/test-dataset',
        ]:
            args = ['import', '--create-dataset', dataset_path, file_]
            imports, ds = self._test_import_file(args)
            self.assertEqual(ds.filename, 'test-dataset')
            # should be a manifest with a single file
            self.assertEqual(len(imports[0].manifest['files']), 1)

    def test_import_remote_file(self):
        args = ['import', '--create-dataset', '--tag', 'hello',
                '--remote-source', 'solvebio:mock_vault:/test-dataset',
                '/this/is/a/remote/file', '/this/remote/*/path']

        imports, ds = self._test_import_file(args)
        self.assertEqual(ds.full_path, 'solvebio:mock_vault:/test-dataset')
        self.assertEqual(ds.tags, ['hello'])
        # should be two imports
        self.assertEqual(len(imports), 2)
        for import_ in imports:
            self.assertEqual(import_['object_id'], 100)
            self.assertTrue('manifest' not in import_)

    def test_import_file_template(self):
        template_path = os.path.join(os.path.dirname(__file__),
                                     "data/template.json")

        args = ['import', '--create-dataset', '--tag', 'hello',
                '--template-file', template_path,
                '--remote-source', 'solvebio:mock_vault:/test-dataset',
                '/this/is/a/remote/file']

        imports, ds = self._test_import_file(args)
        self.assertEqual(ds.full_path, 'solvebio:mock_vault:/test-dataset')
        self.assertEqual(ds.tags, ['hello'])
        self.assertEqual(len(imports), 1)
        import_ = imports[0]
        self.assertEqual(import_['object_id'], 100)
        self.assertTrue('manifest' not in import_)

        with open(template_path, 'r') as fp:
            template = json.load(fp)
        for key in ['reader_params', 'annotator_params',
                    'validation_params', 'entity_params']:
            self.assertEqual(import_[key], template[key])


class UploadTests(CLITests):
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


class DownloadTests(CLITests):
    @mock.patch('solvebio.resource.Object.all')
    @mock.patch(
        'solvebio.resource.apiresource.DownloadableAPIResource.download'
    )
    def _test_download_file(self, args, Download, ObjectAll,
                            download_success=True):
        ObjectAll.side_effect = fake_object_all

        if download_success:
            Download.side_effect = lambda x: True
        else:
            Download.side_effect = Exception('Mock Download Fail')

        # returns (imports_list, dataset)
        return main.main(args)

    def test_download_file(self):
        args = ['download', 'solvebio:mock_vault:/test-file', '.']
        self._test_download_file(args)
        self.assertFalse(os.path.exists('.test-file'))

        args = ['download', 'solvebio:mock_vault:/test-file/*', '.']
        self._test_download_file(args)
        self.assertFalse(os.path.exists('.test-file'))

        # args needed
        args = ['download']
        with self.assertRaises(SystemExit):
            self._test_download_file(args)

        # full path required
        args = ['download', 'mypath']
        with self.assertRaises(SystemExit):
            self._test_download_file(args)

        # local path required
        args = ['download', 'my-vault:/mypath']
        with self.assertRaises(SystemExit):
            self._test_download_file(args)

        args = ['download', 'solvebio:mock_vault:/test-file/*', '.']
        with self.assertRaises(Exception):
            self._test_download_file(args, download_success=False)


class QueueTests(CLITests):
    def test_show_queue(self):
        """Simple test to print the queue"""
        main.main(['queue'])
