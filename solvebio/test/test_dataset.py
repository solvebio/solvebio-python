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

        check_fields = ['class_name', 'created_at',
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
        dataset = self.client.Dataset.get_by_full_path(
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
        expected = """

| Field                        | Data Type   | Entity Type   | Description   |
|------------------------------+-------------+---------------+---------------|
| accession_numbers            | string      |               |               |
| approved_name                | string      |               |               |
| approved_symbol              | string      | gene          |               |
| ccds_ids                     | string      |               |               |
| chromosome                   | string      |               |               |
| date_approved                | date        |               |               |
| date_modified                | date        |               |               |
| date_name_changed            | date        |               |               |
| date_symbol_changed          | date        |               |               |
| ensembl_gene_id              | string      |               |               |
| ensembl_id_ensembl           | string      |               |               |
| entrez_gene_id               | string      |               |               |
| entrez_gene_id_ncbi          | string      |               |               |
| enzyme_ids                   | string      |               |               |
| gene_family_description      | string      |               |               |
| gene_family_tag              | string      |               |               |
| hgnc_id                      | long        |               |               |
| locus                        | string      |               |               |
| locus_group                  | string      |               |               |
| locus_specific_databases     | string      |               |               |
| locus_type                   | string      |               |               |
| mouse_genome_database_id     | long        |               |               |
| mouse_genome_database_id_mgi | long        |               |               |
| name_synonyms                | string      |               |               |
| omim_id_ncbi                 | string      |               |               |
| omim_ids                     | long        |               |               |
| previous_names               | string      |               |               |
| previous_symbols             | string      |               |               |
| pubmed_ids                   | string      |               |               |
| rat_genome_database_id_rgd   | long        |               |               |
| record_type                  | string      |               |               |
| refseq_id_ncbi               | string      |               |               |
| refseq_ids                   | string      |               |               |
| specialist_database_id       | blob        |               |               |
| specialist_database_links    | blob        |               |               |
| status                       | string      |               |               |
| synonyms                     | string      |               |               |
| ucsc_id_ucsc                 | string      |               |               |
| uniprot_id_uniprot           | string      |               |               |
| vega_ids                     | string      |               |               |
"""
        self.assertEqual("{0}".format(fields), expected[1:-1])

    def test_dataset_facets(self):
        dataset = self.client.Dataset.get_by_full_path(
            self.TEST_DATASET_FULL_PATH)
        field = dataset.fields('status')
        facets = field.facets()
        self.assertTrue(len(facets['facets']) >= 0)

    """
    # TODO support a Genomic test dataset (grab clinvar one from API build)
    def test_dataset_beacon(self):
        obj = Object.get_by_full_path(self.TEST_DATASET_FULL_PATH)
        resp = Dataset.retrieve(obj['dataset_id']).beacon(chromosome="6",
                                                          coordinate=123,
                                                          allele='G')
        self.assertTrue('total' in resp and resp['total'] == 0)
        self.assertTrue('exist' in resp and resp['exist'] == False)
        self.assertTrue('query' in resp and resp['query']['chromosome'] == '6')
        self.assertTrue('query' in resp and resp['query']['allele'] == 'G')
        self.assertTrue('query' in resp and resp['query']['coordinate'] == 123)
    """
