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
        self.assertEqual(migration.commit_mode, 'overwrite')
        self.assertEqual(migration.source_params['filters'],
                         [('my_field', 999)])

    @mock.patch('solvebio.resource.DatasetMigration.create')
    def test_migration_from_query_target_id(self, Create):
        Create.side_effect = fake_migration_create

        source = self.client.Dataset(1)
        target = self.client.Dataset(2)

        query = source\
            .query(limit=10, fields=['my_field'])\
            .filter(my_field=999)
        migration = query.migrate(target=target.id,
                                  commit_mode='overwrite',
                                  follow=False)
        self.assertEqual(migration.source_id, source.id)
        self.assertEqual(migration.target_id, target.id)
        self.assertEqual(migration.commit_mode, 'overwrite')
        self.assertEqual(migration.source_params['filters'],
                         [('my_field', 999)])

    @mock.patch('solvebio.resource.DatasetMigration.create')
    def test_migration_from_query_target_object(self, Create):
        Create.side_effect = fake_migration_create

        source = self.client.Object(1)
        source.dataset_id = source.id
        source.object_type = 'dataset'
        target = self.client.Object(2)
        target.object_type = 'dataset'

        query = source\
            .query(limit=10, fields=['my_field'])\
            .filter(my_field=999)
        migration = query.migrate(target=target,
                                  commit_mode='overwrite',
                                  follow=False)
        self.assertEqual(migration.source_id, source.id)
        self.assertEqual(migration.target_id, target.id)
        self.assertEqual(migration.commit_mode, 'overwrite')
        self.assertEqual(migration.source_params['filters'],
                         [('my_field', 999)])

    @mock.patch('solvebio.resource.DatasetMigration.create')
    def test_migration_from_query_target_object_id(self, Create):
        Create.side_effect = fake_migration_create

        source = self.client.Dataset(1)
        target = self.client.Object(2, object_type='dataset')

        query = source\
            .query(limit=10, fields=['my_field'])\
            .filter(my_field=999)
        migration = query.migrate(target=target.id,
                                  commit_mode='overwrite',
                                  follow=False)
        self.assertEqual(migration.source_id, source.id)
        self.assertEqual(migration.target_id, target.id)
        self.assertEqual(migration.commit_mode, 'overwrite')
        self.assertEqual(migration.source_params['filters'],
                         [('my_field', 999)])

    @mock.patch('solvebio.resource.DatasetMigration.create')
    def test_migration_target_dataset_id(self, Create):
        Create.side_effect = fake_migration_create

        source = self.client.Dataset(1)
        target = self.client.Dataset(2)
        migration = source.migrate(target=target.id, follow=False)
        self.assertEqual(migration.source_id, source.id)
        self.assertEqual(migration.target_id, target.id)
        self.assertEqual(migration.commit_mode, 'append')

    @mock.patch('solvebio.resource.DatasetMigration.create')
    def test_migration_target_dataset_dataset(self, Create):
        """Target is a Dataset object"""
        Create.side_effect = fake_migration_create

        source = self.client.Dataset(1)
        target = self.client.Dataset(2)
        migration = source.migrate(target=target, follow=False)
        self.assertEqual(migration.source_id, source.id)
        self.assertEqual(migration.target_id, target.id)
        self.assertEqual(migration.commit_mode, 'append')

    @mock.patch('solvebio.resource.DatasetMigration.create')
    def test_migration_target_dataset_object(self, Create):
        """Target is an Object of object_type=dataset"""
        Create.side_effect = fake_migration_create

        source = self.client.Object(1, object_type='dataset')
        source.dataset_id = source.id
        target = self.client.Object(2, object_type='dataset')
        target.dataset_id = target.id
        migration = source.migrate(target=target, follow=False)
        self.assertEqual(migration.source_id, source.id)
        self.assertEqual(migration.target_id, target.id)
        self.assertEqual(migration.commit_mode, 'append')

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
        self.assertEqual(migration.source_id, source.id)
        self.assertEqual(migration.target_id, target.id)
