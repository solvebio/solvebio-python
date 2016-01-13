from __future__ import absolute_import
from solvebio.resource import Dataset

from .helper import SolveBioTestCase


class LookupTests(SolveBioTestCase):

    def test_lookup(self):
        dataset = Dataset.retrieve('ClinVar/3.7.0-2015-12-06/Variants')

        lookup = dataset.lookup('test')

        # Check that incorrect lookup results in empty list.
        self.assertEqual(lookup, [])

        lookup = dataset.lookup('test', 'nothing')

        # Check that incorrect lookup results in empty list.
        self.assertEqual(lookup, [])

        final_lookup_one = [{u'allele': u'T',
                         u'allele_origin': [u'germline'],
                         u'alternate_allele': [u'T'],
                         u'clinical_channel': None,
                         u'clinical_significance': u'Uncertain significance',
                         u'database_source':
                         [{u'database': u'MedGen',
                            u'database_id': [u'CN221809']}],
                         u'entrez_id_gene': [u'201163'],
                         u'gene_symbol': [u'FLCN'],
                         u'genomic_coordinates': {u'build': u'GRCh37',
                                                    u'chromosome': u'17',
                                                    u'start': 17124835,
                                                    u'stop': 17124835},
                         u'hgvs': u'NC_000017.10:g.17124835A>T',
                         u'id': [u'rs116643153'],
                         u'phenotype': u'not provided',
                         u'rcv_accession': u'RCV000034794',
                         u'rcv_accession_full': u'RCV000034794.1',
                         u'rcv_accession_version': 1,
                         u'reference_allele': u'A',
                         u'review_status': u'no assertion criteria provided',
                         u'review_status_star': 0,
                         u'rs_id': [u'rs116643153'],
                         u'sbid': u'173fba888c03c9db1408154a9de8997e',
                         u'variant_type': u'SNV'}]  # noqa

        # Check that lookup with specific sbid is correct.
        lookup_one = dataset.lookup('173fba888c03c9db1408154a9de8997e')

        self.assertEqual(lookup_one, final_lookup_one)

        final_lookup_two = [{u'allele': u'T',
                           u'allele_origin': [u'somatic'],
                           u'alternate_allele': [u'T'],
                           u'clinical_channel': None,
                           u'clinical_significance': u'not provided',
                           u'database_source': [{u'database': u'GeneReviews',
                                             u'database_id': [u'NBK1247']},
                                            {u'database': u'MedGen',
                                             u'database_id': [u'C0346153']},
                                               {u'database': u'OMIM',
                                                u'database_id': [u'114480']},
                                               {u'database': u'SNOMED_CT',
                                                u'database_id':
                                                    [u'254843006']}],
                           u'entrez_id_gene': [u'100616132', u'2064'],
                           u'gene_symbol': [u'MIR4728', u'ERBB2'],
                           u'genomic_coordinates': {u'build': u'GRCh37',
                                                       u'chromosome': u'17',
                                                       u'start': 37881299,
                                                       u'stop': 37881299},
                           u'hgvs': u'NC_000017.10:g.37881299C>T',
                           u'id': [u'rs104886007'],
                           u'phenotype': u'Familial cancer of breast',
                           u'rcv_accession': u'RCV000119345',
                           u'rcv_accession_full': u'RCV000119345.1',
                           u'rcv_accession_version': 1,
                           u'reference_allele': u'C',
                           u'review_status': u'no assertion provided',
                           u'review_status_star': 0,
                           u'rs_id': [u'rs104886007'],
                           u'sbid': u'17438989fd5f85709b5c4c7a837bc5e0',
                           u'variant_type': u'SNV'}]  # noqa

        # Check that lookup with specific sbid is correct.
        lookup_two = dataset.lookup('17438989fd5f85709b5c4c7a837bc5e0')

        self.assertEqual(lookup_two, final_lookup_two)

        joint_lookup = dataset.lookup('173fba888c03c9db1408154a9de8997e',
                                      '17438989fd5f85709b5c4c7a837bc5e0')

        # Check that combining sbids returns list of correct results.
        self.assertEqual(joint_lookup[0], final_lookup_one[0])
        self.assertEqual(joint_lookup[1], final_lookup_two[0])
