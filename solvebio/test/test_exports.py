from __future__ import absolute_import
import mock

from solvebio.test.client_mocks import fake_export_create

from .helper import SolveBioTestCase


class TestDatasetExports(SolveBioTestCase):

    def _validate_export(self, export, dataset, **kwargs):
        self.assertEqual(export.dataset_id, dataset.id)

    @mock.patch('solvebio.resource.DatasetExport.create')
    def test_export_from_query(self, Create):
        Create.side_effect = fake_export_create

        # Test with params
        params = {
            'fields': ['my_field'],
            'limit': 100,
        }
        target_fields = [dict(name='test')]

        dataset = self.client.Dataset(1)
        export = dataset.export(
            params=params,
            dataset=dataset,
            target_fields=target_fields,
            target_full_path='~/hello',
            format='tsv.gz',
            follow=False
        )
        self.assertEqual(export.dataset_id, dataset.id)
        self.assertEqual(export.target_fields, target_fields)
        self.assertEqual(export.target_full_path, '~/hello')
        self.assertEqual(export.format, 'tsv.gz')
        for k in ['fields', 'limit']:
            self.assertEqual(export.params[k], params[k])
