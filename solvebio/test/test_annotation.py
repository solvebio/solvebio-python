import unittest
import sys

import unittest

import solvebio
from solvebio import Annotation

class AnnotationTest(unittest.TestCase):

    def test_annotation(self):
        self.assertEqual(Annotation.class_url(), '/v1/annotations',
                         'Annotation.class_url()')

        expect = [
            ('class_name', 'Annotation'),
            ('created_at', '2014-09-11T22:01:16.184Z'),
            ('download_url',
             'https://api.solvebio.com/v1/annotations/1/download'),
            ('id'          , 1)
            ]

        # a = Annotation.retrieve(1)
        # FIXME
        # subset = [(key, a[key]) for
        #           key in ['class_name', 'created_at', 'download_url', 'id']]
        # self.assertEqual(subset, expect, 'Annotation.retrieve(1)')


if __name__ == "__main__":
    unittest.main()
