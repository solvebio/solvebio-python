# -*- coding: utf-8 -*-
from __future__ import absolute_import

import unittest
import mock
import json

from solvebio import Dataset


class FakeMigrationResponse():
    status_code = 201

    def __init__(self, data):
        # Set the default properties of DatasetMigration
        self.object = {
            'class_name': 'DatasetMigration',
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

    def json(self):
        return self.object


def fake_migration_request(*args, **kwargs):
    data = json.loads(kwargs['data'])
    return FakeMigrationResponse(data)


class TestDatasetMigrations(unittest.TestCase):

    @mock.patch('solvebio.client.Session.request',
                side_effect=fake_migration_request)
    def test_migration_from_query(self, fake_migration_request):
        source = Dataset(1)
        target = Dataset(2)

        query = source\
            .query(limit=10, fields=['my_field'])\
            .filter(my_field=999)
        migration = query.migrate(target=target, commit_mode='overwrite',
                                  follow=False)
        self.assertEqual(migration.source_id, source.id)
        self.assertEqual(migration.target_id, target.id)
        self.assertEqual(migration.commit_mode, 'overwrite')
        self.assertEqual(migration.source_params['fields'],
                         ['my_field'])
        self.assertEqual(migration.source_params['filters'],
                         [['my_field', 999]])

    @mock.patch('solvebio.client.Session.request',
                side_effect=fake_migration_request)
    def test_migration_from_dataset(self, fake_migration_request):
        source = Dataset(1)
        target = Dataset(2)
        migration = source.migrate(target=target, follow=False)
        self.assertEqual(migration.source_id, source.id)
        self.assertEqual(migration.target_id, target.id)

        # Test with source_params
        source_params = {
            'fields': ['my_field']
        }
        migration = source.migrate(
            target=target, source_params=source_params,
            commit_mode='overwrite', follow=False)
        self.assertEqual(migration.commit_mode, 'overwrite')
        self.assertEqual(migration.source_params['fields'],
                         source_params['fields'])
