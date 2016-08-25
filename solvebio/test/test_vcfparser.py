from __future__ import absolute_import
import os

from .helper import SolveBioTestCase


class VCFParserTest(SolveBioTestCase):

    def test_vcfparser(self):
        from solvebio.contrib.vcf_parser.vcf_parser import ExpandingVCFParser

        expected_fields = (
            'genomic_coordinates',
            'variant',
            'allele',
            'row_id',
            'reference_allele',
            'alternate_alleles',
            'info',
            'qual',
            'filter',
        )

        path = os.path.join(os.path.dirname(__file__),
                            "data/sample.vcf.gz")

        infile = open(path, 'rb')
        parser = ExpandingVCFParser(infile, genome_build='GRCh37')
        # Test that the keys exist and that certain fields are always set
        # Also test that allele expansion is working
        for row in parser:
            self.assertEqual(set(expected_fields), set(row.keys()))
            self.assertTrue(row['genomic_coordinates'])
            self.assertTrue(row['variant'])
            # Ensure 1 allele per row
            self.assertEqual(len(row['allele']), 1)
