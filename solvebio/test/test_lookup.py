from __future__ import absolute_import
from solvebio.resource import Dataset

from .helper import SolveBioTestCase


class LookupTests(SolveBioTestCase):
    # Using new version of HGNC for testing lookup
    # becuase original test dataset did not contain sbids.
    TEST_DATASET_NAME = 'HGNC/2.1.2-2016-01-11/HGNC'

    def setUp(self):
        super(LookupTests, self).setUp()
        self.dataset = Dataset.retrieve(self.TEST_DATASET_NAME)

    final_lookup_one = [{u'ccds_id': None,
                           u'cytogenetic_location': u'19q13.43',
                           u'date_approved': u'2009-07-20',
                           u'date_modified': u'2013-06-27',
                           u'date_name_changed': u'2012-08-15',
                           u'date_symbol_changed': u'2010-11-25',
                           u'ensembl_id_gene': u'ENSG00000268895',
                           u'entrez_id_gene': u'503538',
                           u'genbank_id': [u'BC040926'],
                           u'gene_family': {u'description':
                                            u'Long non-coding RNAs',
                                            u'tag': u'LNCRNA'},
                           u'gene_name': u'A1BG antisense RNA 1',
                           u'gene_name_previous':
                         [u'non-protein coding RNA 181',
                          u'A1BG antisense RNA (non-protein coding)',
                          u'A1BG antisense RNA 1 (non-protein coding)'],
                           u'gene_name_synonym': None,
                           u'gene_symbol': u'A1BG-AS1',
                           u'gene_symbol_previous': [u'NCRNA00181',
                                                     u'A1BGAS',
                                                     u'A1BG-AS'],
                           u'gene_symbol_synonym': [u'FLJ23569'],
                           u'hgnc_id': u'37133',
                           u'intenz_id_enzyme': None,
                           u'locus_information': {u'group': u'non-coding RNA',
                           u'type': u'RNA, long non-coding'},
                           u'locus_specific_database': None,
                           u'mgi_id': None,
                           u'omim_id': None,
                           u'pubmed_id': None,
                           u'refseq_id_gene': u'NR_015380',
                           u'rgd_id': None,
                           u'sbid': u'37133',
                           u'specialist_database': None,
                           u'status': u'Approved',
                           u'ucsc_id': u'uc002qsg.3',
                           u'uniprot_id': None,
                           u'vega_id': u'OTTHUMG00000183508'}]  # noqa

    final_lookup_two = [{u'ccds_id': None,
                           u'cytogenetic_location': u'12p13.31',
                           u'date_approved': u'2012-06-23',
                           u'date_modified': u'2014-08-08',
                           u'date_name_changed': u'2014-08-08',
                           u'date_symbol_changed': None,
                           u'ensembl_id_gene': u'ENSG00000245105',
                           u'entrez_id_gene': u'144571',
                           u'genbank_id': None,
                           u'gene_family': {u'description':
                           u'Long non-coding RNAs', u'tag': u'LNCRNA'},
                           u'gene_name': u'A2M antisense RNA 1 (head to head)',
                           u'gene_name_previous':
                          [u'A2M antisense RNA 1 (non-protein coding)',
                                                      u'A2M antisense RNA 1'],
                           u'gene_name_synonym': None,
                           u'gene_symbol': u'A2M-AS1',
                           u'gene_symbol_previous': None,
                           u'gene_symbol_synonym': None,
                           u'hgnc_id': u'27057',
                           u'intenz_id_enzyme': None,
                           u'locus_information': {u'group': u'non-coding RNA',
                           u'type': u'RNA, long non-coding'},
                           u'locus_specific_database': None,
                           u'mgi_id': None,
                           u'omim_id': None,
                           u'pubmed_id': None,
                           u'refseq_id_gene': u'NR_026971',
                           u'rgd_id': None,
                           u'sbid': u'27057',
                           u'specialist_database': None,
                           u'status': u'Approved',
                           u'ucsc_id': u'uc009zgj.1',
                           u'uniprot_id': None,
                           u'vega_id': u'OTTHUMG00000168289'}]  # noqa

    def test_lookup_error(self):
        lookup_one = self.dataset.lookup('test')
        lookup_two = self.dataset.lookup('test', 'nothing')
        # Check that incorrect lookup results in empty list.
        self.assertEqual(lookup_one, [])
        self.assertEqual(lookup_two, [])

    def test_lookup_correct(self):
        sbid_one = '37133'
        sbid_two = '27057'
        lookup_one = self.dataset.lookup(sbid_one)
        lookup_two = self.dataset.lookup(sbid_two)
        # Check that lookup with specific sbid is correct.
        self.assertEqual(lookup_one, self.final_lookup_one)
        self.assertEqual(lookup_two, self.final_lookup_two)

        joint_lookup = self.dataset.lookup(sbid_one, sbid_two)

        # Check that combining sbids returns list of correct results.
        self.assertEqual(joint_lookup[0], self.final_lookup_one[0])
        self.assertEqual(joint_lookup[1], self.final_lookup_two[0])
