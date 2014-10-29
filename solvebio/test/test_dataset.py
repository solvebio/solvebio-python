from solvebio.resource import Dataset

from .helper import SolveBioTestCase


class DatasetTests(SolveBioTestCase):
    """
    Test Dataset, DatasetField, and Facets
    """

    def test_dataset_retrieval(self):
        dataset = Dataset.retrieve(self.TEST_DATASET_NAME)
        self.assertTrue('id' in dataset,
                        'Should be able to get id in dataset')

        check_fields = set(['class_name', 'created_at',
                            'data_url',
                            'depository', 'depository_id',
                            'depository_version', 'depository_version_id',
                            'description',
                            'fields_url', 'full_name',
                            'id', 'name', 'title', 'updated_at',
                            'url'])
        self.assertSetEqual(set(dataset.keys()), check_fields)

    def test_dataset_fields(self):
        fields = Dataset.retrieve(self.TEST_DATASET_NAME).fields()
        dataset_field = fields.data[0]
        self.assertTrue('id' in dataset_field,
                        'Should be able to get id in list of dataset fields')

        check_fields = set(['class_name', 'created_at',
                            'data_type', 'dataset', 'dataset_id',
                            'description', 'facets_url',
                            'full_name', 'id',
                            'name', 'updated_at',
                            'url'])
        self.assertSetEqual(set(dataset_field.keys()), check_fields)

    def test_dataset_facets(self):
        field = Dataset.retrieve(self.TEST_DATASET_NAME).fields('hgnc_id')
        facets = field.facets()
        self.assertTrue(facets.total >= 0,
                        'facet should have an total field >= 0')
