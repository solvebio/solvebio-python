# -*- coding: utf-8 -*-
from __future__ import absolute_import

import unittest
import mock

from solvebio import Dataset
from solvebio.test.client_mocks import fake_migration_create


class TestDatasetMigrations(unittest.TestCase):

    @mock.patch('solvebio.resource.DatasetMigration.create',
                side_effect=fake_migration_create)
    def test_migration_from_query(self, fake_migration_create):
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
                         [('my_field', 999)])

    @mock.patch('solvebio.resource.DatasetMigration.create',
                side_effect=fake_migration_create)
    def test_migration_from_dataset(self, fake_migration_create):
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
