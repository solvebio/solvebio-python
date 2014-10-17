import unittest
import os

from solvebio.resource import Annotation


@unittest.skipUnless('TEST_SOLVEBIO_API_UPDATE' in os.environ,
                     'Annotation Update')
class AnnotationAccessTest(unittest.TestCase):

    def test_annotation(self):
        self.assertEqual(Annotation.class_url(), '/v1/annotations',
                         'Annotation.class_url()')

        all = Annotation.all()
        self.assertTrue(all.total > 1,
                        "Annotation.all() returns more than one value")
        return

if __name__ == "__main__":
    unittest.main()
