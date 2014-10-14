import unittest
import sys
import os

from solvebio import Sample, SolveError

class SampleTest(unittest.TestCase):

    def test_sample_error_params(self):
        for params in [ (), ('hg19') ]:
            self.assertRaises(TypeError, lambda: Sample.create(*params))
            self.assertRaises(TypeError, lambda: Sample.create_from_file(*params))
            self.assertRaises(TypeError, lambda: Sample.create_from_url(*params))
        for params in [ {},  {'vcf_file':'a', 'vcf_url':'b'} ]:
            self.assertRaises(TypeError, lambda: Sample.create('hg19', *params))


    def test_sample(self):
        self.assertEqual(Sample.class_url(), '/v1/samples',
                         'Sample.class_url()')

        if 'SOLVEBIO_API_KEY' in os.environ and \
               os.environ['SOLVEBIO_API_KEY'].startswith('0cedb161d'):
            self.assertRaises(SolveError, lambda: Sample.retrieve(1))
        # FIXME:
        # expect = [
        #     ('class_name', 'Sample'),
        #     ('annotations_count', 4),
        #     ('id'          , 1),
        #     ('description' , ''),
        #     ('genome_build' , 'hg19'),
        #     ('vcf_md5'      , 'a03e39e96671a01208cffd234812556d'),
        #     ('vcf_size'     , 12124),
        #     ]
        # a = Sample.retrieve(1)
        # subset = [(key, a[key]) for
        #           key in [x[0] for x in expect]]
        # self.assertEqual(subset, expect, 'Sample.retrieve(1)')

        all = Sample.all()
        self.assertTrue(len(all) > 1,
                        "Sample.all() returns more than one value")


if __name__ == "__main__":
    unittest.main()
