import unittest
import sys

from solvebio import Annotation

class AnnotationTest(unittest.TestCase):

    def test_annotation(self):
        self.assertEqual(Annotation.class_url(), '/v1/annotations',
                         'Annotation.class_url()')

        expect = [
            ('class_name', 'Annotation'),
            ('created_at', '2014-09-11T22:01:16.184Z'),
            # ('download_url',
            #  'https://api.solvebio.com/v1/annotations/1/download'),
            ('id'          , 1),
            ('sample_id'   , 1),
            ('status'      , 'completed')
            ]
        a = Annotation.retrieve(1)
        print a
        subset = [(key, a[key]) for
                  key in [x[0] for x in expect]]
        self.assertEqual(subset, expect, 'Annotation.retrieve(1)')

        all = Annotation.all()
        self.assertTrue(len(a) > 1,
                        "Annotation.all() returns more than one value")


if __name__ == "__main__":
    unittest.main()
