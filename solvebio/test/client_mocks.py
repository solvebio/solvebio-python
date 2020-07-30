# -*- coding: utf-8 -*-
from __future__ import absolute_import

from solvebio.resource.solveobject import convert_to_solve_object


class Fake201Response(object):
    status_code = 201
    class_name = None

    def __init__(self, data):
        self.object = {
            'id': data.get('id', 100),
            'class_name': self.class_name
        }

    def json(self):
        return self.object

    def create(self, *args, **kwargs):
        return convert_to_solve_object(self.object)

    def save(self, *args, **kwargs):
        return self.create(*args, **kwargs)

    def retrieve(self, r_id, *args, **kwargs):
        obj = self.create()
        obj.id = r_id
        return obj

    def _retrieve_helper(self, model_name, field_name, error_value,
                         *args, **kwargs):
        obj = self.create()
        for k, v in kwargs.items():
            obj[k] = v

        return obj

    def all(self, *args, **kwargs):
        class ExtendedList(list):
            def solve_objects(self):
                return convert_to_solve_object(self)

        return ExtendedList([self.create()])

    def update_paths(self):
        """Sets vault_name, path and full_path based on mock inputs"""
        if not self.object['vault_name']:
            self.object['vault_name'] = 'mock_vault'

        if not self.object['path']:
            self.object['path'] = '/{0}'.format(
                self.object.get(
                    'filename', self.object.get('vault_object_filename'))
            )

        if not self.object['full_path']:
            self.object['full_path'] = 'solvebio:{0}:{1}'.format(
                self.object['vault_name'], self.object['path'])

    def update_dataset(self):
        """Sets dataset_id if object is a dataset"""
        if self.object['object_type'] == 'dataset':
            self.object['dataset_id'] = self.object['id']


class FakeMigrationResponse(Fake201Response):

    class_name = 'DatasetMigration'

    def __init__(self, data):
        # Set the default properties of DatasetMigration
        self.object = {
            'class_name': self.class_name,
            'id': 100,
            'commit_mode': 'append',
            'source': dict(id=data.get('source_id')),
            'source_params': {
                "fields": None,
                "route": None,
                "exclude_fields": None,
                "filters": None,
                "limit": None,
                "debug": False
            },
            'target': dict(id=data.get('target_id')),
            'target_fields': [],
            'include_errors': False,
        }
        self.object.update(data)


class FakeExportResponse(Fake201Response):

    class_name = 'DatasetExport'

    def __init__(self, data):
        # Set the default properties of DatasetExport
        self.object = {
            'class_name': self.class_name,
            'id': 100,
            'target_fields': [],
            'documents_count': 0,
            'dataset_id': data.get('dataset_id'),
            'dataset': dict(id=data.get('dataset_id')),
            'params': {
                "fields": None,
                "exclude_fields": None,
                "entities": None,
                "genome_build": None,
                "limit": None,
                "filters": None,
                "offset": None,
                "query": None,
                "debug": False
            },
            'annotator_params': [],
            'metadata': {},
        }
        self.object.update(data)


class FakeVaultResponse(Fake201Response):

    class_name = 'Vault'

    def __init__(self, data):
        self.object = {
            'class_name': self.class_name,
            'name': 'test_vault',
            'require_unique_paths': True,
            'vault_type': 'general',
            'provider': 'SolveBio',
            'id': 100,
            'full_path': 'solvebio:test_vault'
        }
        self.object.update(data)


class FakeObjectResponse(Fake201Response):

    class_name = 'Object'

    def __init__(self, data):
        self.object = {
            'class_name': self.class_name,
            'id': 100,
            'parent_object_id': 99,
            'path': None,
            'full_path': None,
            'upload_url': None,
            'size': None,
            'md5': None,
            'filename': 'file.json.gz',
            'path': None,
            'full_path': None,
            'vault_name': None,
            'vault_id': None,
            'object_type': 'folder',
            'tags': [],
        }
        self.object.update(data)
        self.update_paths()
        self.update_dataset()


class FakeDatasetResponse(Fake201Response):

    class_name = 'Dataset'

    def __init__(self, data):

        # Override default object options
        overrides = {
            'object_type': 'dataset',
            'filename': data.get('name', 'test-dataset'),
            'vault_object_name': data.get('name', 'test-dataset'),
            'path': None,
            'full_path': None,
            'class_name': self.class_name,
        }
        data.update(overrides)
        self.object = FakeObjectResponse(data).object
        self.update_paths()


class FakeDatasetTemplateResponse(Fake201Response):

    class_name = 'DatasetTemplate'

    def __init__(self, data):
        self.object = {
            'class_name': self.class_name,
            'name': None,
            'id': 100,
            'vault_parent_object_id': 99,
            'account': {
                'name': None,
                'domain': None,
            },
            'fields': None,
            'entity_type': None,
            'validation_params': None,
            'entity_params': None,
            'reader_params': None,
            'annotator_params': None,
        }
        self.object.update(data)


class FakeDatasetTask(Fake201Response):

    class_name = 'DatasetTask'

    def __init__(self, data):
        self.object = {
            'class_name': self.class_name,
            'vault_id': None,
            'id': 100,
            'status': 'completed',
            'dataset': FakeDatasetResponse(dict(name='fake_dataset')).object,  # noqa
            'account': {
                'name': None,
                'domain': None,
            },
        }
        self.object.update(data)


class FakeDatasetImport(FakeDatasetTask):

    class_name = 'DatasetImport'

    def __init__(self, data):
        super(FakeDatasetImport, self).__init__(data)
        self.object['dataset_commits'] = []


def fake_vault_create(*args, **kwargs):
    return FakeVaultResponse(kwargs).create()


def fake_vault_all(*args, **kwargs):
    return FakeVaultResponse(kwargs).all()


def fake_object_all(*args, **kwargs):
    return FakeObjectResponse(kwargs).all()


def fake_object_create(*args, **kwargs):
    return FakeObjectResponse(kwargs).create()


def fake_object_save(*args, **kwargs):
    return FakeObjectResponse(kwargs).save()


def fake_object_retrieve(*args, **kwargs):
    return FakeObjectResponse(kwargs)._retrieve_helper(
        'LogicalObject', *args, **kwargs)


def fake_dataset_create(*args, **kwargs):
    # Dataset.create() is deprecated
    print("WARNING: Your code likely wants to be using FakeObjectCreate.")
    return FakeDatasetResponse(kwargs).create()


def fake_dataset_get_or_create(*args, **kwargs):
    from solvebio.resource import Object
    dataset_obj = FakeObjectResponse(kwargs).create()

    # Dataset.create requires a full_path, override with this
    full_path, path_dict = Object.validate_full_path(args[0])
    dataset_obj.name = path_dict['filename']
    dataset_obj.path = path_dict['path']
    dataset_obj.full_path = full_path
    return FakeDatasetResponse(dict(dataset_obj)).create()


def fake_dataset_import_create(*args, **kwargs):
    return FakeDatasetImport(kwargs).create()


def fake_dataset_tmpl_create(*args, **kwargs):
    return FakeDatasetTemplateResponse(kwargs).create()


def fake_dataset_tmpl_retrieve(rid, *args, **kwargs):
    return FakeDatasetTemplateResponse(kwargs).retrieve(rid)


def fake_migration_create(*args, **kwargs):
    return FakeMigrationResponse(kwargs).create()


def fake_export_create(*args, **kwargs):
    return FakeExportResponse(kwargs).create()
