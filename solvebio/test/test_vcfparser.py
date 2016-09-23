from __future__ import absolute_import

import os
import io

from .helper import SolveBioTestCase


class VCFParserTest(SolveBioTestCase):
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

    def test_vcfparser_from_filename(self):
        from solvebio.contrib.vcf_parser.vcf_parser import ExpandingVCFParser

        path = os.path.join(os.path.dirname(__file__),
                            "data/sample.vcf.gz")
        parser = ExpandingVCFParser(filename=path, genome_build='GRCh37')
        # Test that the keys exist and that certain fields are always set
        # Also test that allele expansion is working
        for row in parser:
            self.assertEqual(set(self.expected_fields), set(row.keys()))
            self.assertTrue(row['genomic_coordinates'])
            self.assertTrue(row['variant'])
            # Ensure 1 allele per row
            self.assertEqual(len(row['allele']), 1)

        parser.close()

    def test_vcfparser_from_fsock(self):
        from solvebio.contrib.vcf_parser.vcf_parser import ExpandingVCFParser

        path = os.path.join(os.path.dirname(__file__),
                            "data/sample.vcf.gz")
        infile = io.open(path, 'rb')
        parser = ExpandingVCFParser(fsock=infile, genome_build='GRCh37')
        # Test that the keys exist and that certain fields are always set
        # Also test that allele expansion is working
        for row in parser:
            self.assertEqual(set(self.expected_fields), set(row.keys()))
            self.assertTrue(row['genomic_coordinates'])
            self.assertTrue(row['variant'])
            # Ensure 1 allele per row
            self.assertEqual(len(row['allele']), 1)

        parser.close()
