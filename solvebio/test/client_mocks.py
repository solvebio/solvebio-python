# -*- coding: utf-8 -*-
from __future__ import absolute_import

from solvebio.resource.solveobject import convert_to_solve_object


class Fake201Response():
    status_code = 201
    class_name = None

    def __init__(self, data):
        self.object = {
            'id': 100,
            'class_name': self.class_name,
        }

    def json(self):
        return self.object

    def create(self, *args, **kwargs):
        return convert_to_solve_object(self.object)

    def retrieve(self, r_id, *args, **kwargs):
        obj = self.create()
        obj.id = r_id
        return obj


class FakeMigrationResponse(Fake201Response):

    class_name = 'DatasetMigration'

    def __init__(self, data):
        # Set the default properties of DatasetMigration
        self.object = {
            'class_name': self.class_name,
            'id': 100,
            'commit_mode': 'append',
            'source': None,
            'source_params': {
                "fields": None,
                "route": None,
                "exclude_fields": None,
                "filters": None,
                "limit": None,
                "debug": False
            },
            'target': None,
            'target_fields': [],
            'include_errors': False,
            'auto_approve': False,
        }
        self.object.update(data)


class FakeDepositoryResponse(Fake201Response):

    class_name = 'Depository'

    def __init__(self, data):
        self.object = {
            'class_name': self.class_name,
            'full_name': None,
            'name': None,
            'id': 100,
            'account': {
                'name': None,
                'domain': None,
            },
        }
        self.object.update(data)


class FakeDepositoryVersionResponse(Fake201Response):

    class_name = 'DepositoryVersion'

    def __init__(self, data):
        self.object = {
            'class_name': self.class_name,
            'depository_id': None,
            'full_name': None,
            'name': None,
            'id': 100,
            'account': {
                'name': None,
                'domain': None,
            },
        }
        self.object.update(data)


class FakeDatasetResponse(Fake201Response):

    class_name = 'Dataset'

    def __init__(self, data):
        self.object = {
            'class_name': self.class_name,
            'full_name': None,
            'name': None,
            'depository_id': None,
            'depository_version_id': None,
            'id': 100,
            'account': {
                'name': None,
                'domain': None,
            },
            'is_genomic': False,
        }
        self.object.update(data)


class FakeDatasetTemplateResponse(Fake201Response):

    class_name = 'DatasetTemplate'

    def __init__(self, data):
        self.object = {
            'class_name': self.class_name,
            'name': None,
            'id': 100,
            'account': {
                'name': None,
                'domain': None,
            },
            'fields': None,
            'entity_type': None,
            'is_genomic': False,
        }
        self.object.update(data)


def fake_depo_create(*args, **kwargs):
    return FakeDepositoryResponse(kwargs).create()


def fake_depo_version_create(*args, **kwargs):
    return FakeDepositoryVersionResponse(kwargs).create()


def fake_dataset_create(*args, **kwargs):
    return FakeDatasetResponse(kwargs).create()


def fake_data_tpl_create(*args, **kwargs):
    return FakeDatasetTemplateResponse(kwargs).create()


def fake_data_tpl_retrieve(rid, *args, **kwargs):
    return FakeDatasetTemplateResponse(kwargs).retrieve(rid)


def fake_migration_create(*args, **kwargs):
    return FakeMigrationResponse(kwargs).create()
