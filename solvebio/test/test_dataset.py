from __future__ import absolute_import

from .helper import SolveBioTestCase


class DatasetTests(SolveBioTestCase):
    """
    Test Dataset, DatasetField, and Facets
    """

    def test_dataset_retrieval(self):
        dataset = self.client.Dataset.get_by_full_path(
            self.TEST_DATASET_FULL_PATH)
        self.assertTrue('id' in dataset,
                        'Should be able to get id in dataset')

        check_fields = ['class_name',
                        'created_at',
                        'data_url',
                        'vault_id',
                        'vault_object_id',
                        'description',
                        'fields_url',
                        'id',
                        'updated_at',
                        'url',
                        'documents_count']

        for f in check_fields:
            self.assertTrue(f in dataset, '{0} field is present'.format(f))

    def test_dataset_tree_traversal_shortcuts(self):
        dataset = self.client.Dataset.get_by_full_path(
            self.TEST_DATASET_FULL_PATH)

        # get vault object
        self.assertEqual(dataset.vault_object.full_path,
                         self.TEST_DATASET_FULL_PATH)

        # get vault object parent
        self.assertEqual(
            dataset.vault_object.parent.full_path,
            '/'.join(self.TEST_DATASET_FULL_PATH.split('/')[:-1])
        )

        # get vault
        self.assertEqual(
            dataset.vault_object.vault.full_path,
            ':'.join(self.TEST_DATASET_FULL_PATH.split(':')[:-1])
        )

    def test_dataset_fields(self):
        dataset = self.client.Object.get_by_full_path(
            self.TEST_DATASET_FULL_PATH)
        fields = dataset.fields()
        dataset_field = fields.data[0]
        self.assertTrue('id' in dataset_field,
                        'Should be able to get id in list of dataset fields')

        check_fields = set(['class_name', 'created_at',
                            'data_type', 'dataset_id', 'title',
                            'description', 'facets_url',
                            'ordering', 'is_hidden', 'is_valid',
                            'is_list', 'entity_type', 'expression',
                            'name', 'updated_at', 'is_read_only',
                            'depends_on',
                            'id', 'url', 'vault_id'])
        self.assertSetEqual(set(dataset_field.keys()), check_fields)

    def test_dataset_facets(self):
        dataset = self.client.Object.get_by_full_path(
            self.TEST_DATASET_FULL_PATH)
        field = dataset.fields('status')
        facets = field.facets()
        self.assertTrue(len(facets['facets']) >= 0)
