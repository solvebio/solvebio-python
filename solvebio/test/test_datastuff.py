"""Test Dataset and DatasetField"""
import unittest
from solvebio.resource import Dataset


class DatasetTest(unittest.TestCase):

    def test_dataset(self):
        datasets = Dataset.all()
        if datasets.total == 0:
            return unittest.skip('no datasets found')
        dataset = datasets.data[0]
        self.assertTrue('id' in dataset,
                        'Should be able to get id in dataset')
        for field in ['class_name', 'created_at',
                      'data_url',
                      'depository', 'depository_id',
                      'depository_version', 'depository_version_id',
                      'description',
                      'fields_url', 'full_name',
                      'name', 'title', 'updated_at',
                      'url']:
            self.assertTrue(field in dataset,
                            "Should find field {0} in dataset {1}"
                            .format(field, dataset.id))
        fields = dataset.fields()
        if fields.total == 0:
            return unittest.skip('no fields of dataset {0} found'
                                 .format(dataset.name))
        dataset_field = fields.data[0]
        self.assertTrue('id' in dataset_field,
                        'Should be able to get id in list of dataset fields')
        for field in ['class_name', 'created_at',
                      'dataset', 'dataset_id',
                      'description', 'facets_url',
                      'name', 'updated_at',
                      'url']:
            self.assertTrue(field in dataset_field,
                            'Should find field {0} in fields {1}'
                            .format(field, dataset_field.id))
        facets = dataset_field.facets()
        self.assertTrue(isinstance(facets.total, int),
                        'facet should have an integer total field')

if __name__ == "__main__":
    unittest.main()
