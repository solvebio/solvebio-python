from __future__ import absolute_import

from .helper import SolveBioTestCase


class LookupTests(SolveBioTestCase):
    # Using new version of HGNC for testing lookup
    # because original test dataset did not contain sbids.
    TEST_DATASET_FULL_PATH = 'solvebio:public:/HGNC/2.1.2-2016-01-11/HGNC'

    final_lookup_one = [{
        '_id': '37133',
        'ccds_id': None,
        'cytogenetic_location': '19q13.43',
        'date_approved': '2009-07-20',
        'date_modified': '2013-06-27',
        'date_name_changed': '2012-08-15',
        'date_symbol_changed': '2010-11-25',
        'ensembl_id_gene': 'ENSG00000268895',
        'entrez_id_gene': '503538',
        'genbank_id': ['BC040926'],
        'gene_family': {
            'description': 'Long non-coding RNAs',
            'tag': 'LNCRNA'
        },
        'gene_name': 'A1BG antisense RNA 1',
        'gene_name_previous': [
            'non-protein coding RNA 181',
            'A1BG antisense RNA (non-protein coding)',
            'A1BG antisense RNA 1 (non-protein coding)'
        ],
        'gene_name_synonym': None,
        'gene_symbol': 'A1BG-AS1',
        'gene_symbol_previous': [
            'NCRNA00181',
            'A1BGAS',
            'A1BG-AS'
        ],
        'gene_symbol_synonym': ['FLJ23569'],
        'hgnc_id': '37133',
        'intenz_id_enzyme': None,
        'locus_information': {
            'group': 'non-coding RNA',
            'type': 'RNA, long non-coding'
        },
        'locus_specific_database': None,
        'mgi_id': None,
        'omim_id': None,
        'pubmed_id': None,
        'refseq_id_gene': 'NR_015380',
        'rgd_id': None,
        'sbid': '37133',
        'specialist_database': None,
        'status': 'Approved',
        'ucsc_id': 'uc002qsg.3',
        'uniprot_id': None,
        'vega_id': 'OTTHUMG00000183508'
    }]  # noqa

    final_lookup_two = [{
        '_id': '27057',
        'ccds_id': None,
        'cytogenetic_location': '12p13.31',
        'date_approved': '2012-06-23',
        'date_modified': '2014-08-08',
        'date_name_changed': '2014-08-08',
        'date_symbol_changed': None,
        'ensembl_id_gene': 'ENSG00000245105',
        'entrez_id_gene': '144571',
        'genbank_id': None,
        'gene_family': {
            'description': 'Long non-coding RNAs', 'tag': 'LNCRNA'
        },
        'gene_name': 'A2M antisense RNA 1 (head to head)',
        'gene_name_previous': [
            'A2M antisense RNA 1 (non-protein coding)',
            'A2M antisense RNA 1'
        ],
        'gene_name_synonym': None,
        'gene_symbol': 'A2M-AS1',
        'gene_symbol_previous': None,
        'gene_symbol_synonym': None,
        'hgnc_id': '27057',
        'intenz_id_enzyme': None,
        'locus_information': {
            'group': 'non-coding RNA',
            'type': 'RNA, long non-coding'
        },
        'locus_specific_database': None,
        'mgi_id': None,
        'omim_id': None,
        'pubmed_id': None,
        'refseq_id_gene': 'NR_026971',
        'rgd_id': None,
        'sbid': '27057',
        'specialist_database': None,
        'status': 'Approved',
        'ucsc_id': 'uc009zgj.1',
        'uniprot_id': None,
        'vega_id': 'OTTHUMG00000168289'
    }]  # noqa

    def setUp(self):
        super(LookupTests, self).setUp()
        self.dataset = self.client.Dataset.get_by_full_path(
            self.TEST_DATASET_FULL_PATH)

    def test_lookup_error(self):
        # Check that incorrect lookup results in empty list.
        lookup_one = self.dataset.lookup('test')
        self.assertEqual(lookup_one, [])

        lookup_two = self.dataset.lookup('test', 'nothing')
        self.assertEqual(lookup_two, [])

    def test_lookup_correct(self):
        # Check that lookup with specific sbid is correct.
        self.maxDiff = 1e6
        sbid_one = '37133'
        lookup_one = self.dataset.lookup(sbid_one)
        self.assertEqual(lookup_one, self.final_lookup_one)

        sbid_two = '27057'
        lookup_two = self.dataset.lookup(sbid_two)
        self.assertEqual(lookup_two, self.final_lookup_two)

        # Check that combining sbids returns list of correct results.
        joint_lookup = self.dataset.lookup(sbid_one, sbid_two)
        self.assertEqual(joint_lookup[0], self.final_lookup_one[0])
        self.assertEqual(joint_lookup[1], self.final_lookup_two[0])
