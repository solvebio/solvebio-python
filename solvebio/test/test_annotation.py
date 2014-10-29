from test_helper import unittest
import os

import solvebio
from solvebio.resource import Annotation, Sample


class AnnotationTest(unittest.TestCase):

    # TODO: check unauthorized access

    # FIXME: DRY routine with test_sample_access.py
    def check_response(self, response, expect, msg):
        subset = [(key, response[key]) for
                  key in [x[0] for x in expect]]
        self.assertEqual(subset, expect, msg)

    @unittest.skipIf(solvebio.api_host == 'https://api.solvebio.com',
                     "annotation creation")
    def test_annotation_create(self):

        vcf_file = os.path.join(os.path.dirname(__file__),
                                "data/sample.vcf.gz")
        my_sample = Sample.create(genome_build='hg19', vcf_file=vcf_file)
        self.assertTrue(my_sample)

        sample_id = my_sample['id']
        expect = [
            ('class_name', 'Annotation'),
            ('error_message', ''),
            ('sample_id', sample_id), ]

        response = Annotation.create(sample_id=sample_id)
        self.check_response(response, expect,
                            'Annotation.create(sample_id={0})'
                            .format(sample_id))
        for field in ['status', 'user_id', 'created_at', 'updated_at']:
            self.assertTrue(field in response,
                            "response has field {0}".format(field))

        all = Annotation.all()
        self.assertTrue(all.total > 1,
                        "Annotation.all() returns more than one value")

        response = my_sample.annotate()
        # FIXME: test annotate() more.

        my_sample.delete()

if __name__ == "__main__":
    unittest.main()
