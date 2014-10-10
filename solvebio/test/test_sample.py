import unittest
import sys

from solvebio import Sample

class SampleTest(unittest.TestCase):

    def test_annotation(self):
        self.assertEqual(Sample.class_url(), '/v1/samples',
                         'Sample.class_url()')

        # FIXME:
        # Hmmm, need to try with something test key has access to.
        # And while we are at it we should also test access denied.
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
                        "Annotation.all() returns more than one value")


if __name__ == "__main__":
    unittest.main()
