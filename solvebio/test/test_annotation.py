import os

import solvebio
from solvebio.resource import Annotation, Sample

from .helper import unittest, SolveBioTestCase


class AnnotationTest(SolveBioTestCase):
    def test_annotation_url(self):
        self.assertEqual(Annotation.class_url(), '/v1/annotations',
                         'Annotation.class_url()')

    @unittest.skipIf(solvebio.api_host == 'https://api.solvebio.com',
                     "annotation creation")
    def test_annotation_crud(self):
        vcf_file = os.path.join(os.path.dirname(__file__),
                                "data/sample.vcf.gz")
        my_sample = Sample.create(genome_build='hg19', vcf_file=vcf_file)
        self.assertTrue(my_sample)

        sample_id = my_sample['id']
        expect = [
            ('class_name', 'Annotation'),
            ('error_message', ''),
            ('sample_id', sample_id), ]

        annotation = Annotation.create(sample_id=sample_id)
        self.check_response(annotation, expect,
                            'Annotation.create(sample_id={0})'
                            .format(sample_id))

        for field in ['status', 'user_id', 'created_at', 'updated_at']:
            self.assertTrue(field in annotation,
                            "Annotation has field {0}".format(field))

        annotation.delete()
        my_sample.delete()
