# -*- coding: utf-8 -*-
from __future__ import absolute_import

import mock

from .helper import SolveBioTestCase

from solvebio.test.client_mocks import fake_migration_create


class TestDatasetMigrations(SolveBioTestCase):

    @mock.patch('solvebio.resource.DatasetMigration.create')
    def test_migration_from_query(self, Create):
        Create.side_effect = fake_migration_create

        source = self.client.Dataset(1)
        target = self.client.Dataset(2)

        query = source\
            .query(limit=10, fields=['my_field'])\
            .filter(my_field=999)
        migration = query.migrate(target=target,
                                  commit_mode='overwrite',
                                  follow=False)
        self.assertEqual(migration.source_id, source.id)
        self.assertEqual(migration.target_id, target.id)

        # validate
        self.assertEqual(migration.source.id, source.id)
        self.assertEqual(migration.target.id, target.id)

        self.assertEqual(migration.commit_mode, 'overwrite')
        self.assertEqual(migration.source_params['fields'],
                         ['my_field'])
        self.assertEqual(migration.source_params['filters'],
                         [('my_field', 999)])

    @mock.patch('solvebio.resource.DatasetMigration.create')
    def test_migration_from_dataset(self, Create):
        Create.side_effect = fake_migration_create

        source = self.client.Dataset(1)
        target = self.client.Dataset(2)
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
