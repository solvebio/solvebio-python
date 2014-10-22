"""Test Dataset, DatasetField, and Facets"""
import unittest
from solvebio.resource import Dataset, DatasetField


class DataStuffTest(unittest.TestCase):

    def test_dataset(self):
        datasets = Dataset.all()
        if datasets.total == 0:
            return unittest.skip('no datasets found')
        # print "datasets.total %s" % [datasets.total]  # compare with ruby
        dataset = datasets.data[0]
        self.assertTrue('id' in dataset,
                        'Should be able to get id in dataset')

        dataset2 = Dataset.retrieve(dataset.id)
        self.assertEqual(dataset, dataset2,
                         "Retrieving dataset id {0} found by all()"
                         .format(dataset.id))

        check_fields = set(['class_name', 'created_at',
                            'data_url',
                            'depository', 'depository_id',
                            'depository_version', 'depository_version_id',
                            'description',
                            'fields_url', 'full_name',
                            'id', 'name', 'title', 'updated_at',
                            'url'])
        self.assertSetEqual(set(dataset.keys()), check_fields)
        fields = dataset.fields()
        if fields.total == 0:
            return unittest.skip('no fields of dataset {0} found'
                                 .format(dataset.name))

        # print "fields.total %s" % [fields.total]  # compare with ruby
        dataset_field = fields.data[0]
        self.assertTrue('id' in dataset_field,
                        'Should be able to get id in list of dataset fields')

        dataset_field2 = DatasetField.retrieve(dataset_field.id)
        self.assertEqual(dataset_field, dataset_field2,
                         "Retrieving DatasetField id {0} found by all()"
                         .format(dataset_field.id))

        check_fields = set(['class_name', 'created_at',
                            'data_type', 'dataset', 'dataset_id',
                            'description', 'facets_url',
                            'full_name', 'id',
                            'name', 'updated_at',
                            'url'])
        self.assertSetEqual(set(dataset_field.keys()), check_fields)

        facets = dataset_field.facets()
        # print "faces.total %s" % [facets.total] #  compare with ruby
        # We can get small or large numbers like 0 or 4902851621.0
        self.assertTrue(facets.total >= 0,
                        'facet should have an total field >= 0')

if __name__ == "__main__":
    unittest.main()
