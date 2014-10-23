import unittest
import tempfile
import os

from solvebio.resource import Annotation
from solvebio.errors import SolveError


class AnnotationAccessTest(unittest.TestCase):

    def test_annotation(self):
        self.assertEqual(Annotation.class_url(), '/v1/annotations',
                         'Annotation.class_url()')

    def test_annotation_download(self):
        all = Annotation.all()
        if all.total == 0:
            return unittest.skip("no annotations found to download")
        ann = all.data[0]
        try:
            response = ann.download(tempfile.tempdir)
            self.assertEqual(response.status_code, 200,
                             "Download annotation file status ok")
            self.assertTrue(os.path.exists(response.filename),
                            "Download annotation file on filesystem")
            os.remove(response.filename)
        except SolveError as err:
            self.assertEqual(err.status_code, 404)


if __name__ == "__main__":
    unittest.main()
