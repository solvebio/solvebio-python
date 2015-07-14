from __future__ import absolute_import
import unittest

from solvebio.resource.util import class_to_api_name


class ConversionTest(unittest.TestCase):
    def test_class_to_api_name(self):
        for class_name, expect in [
                ('Annotation', 'annotations'),
                ('DataField', 'data_fields'),
                ('Depository', 'depositories')]:

            self.assertEqual(class_to_api_name(class_name), expect)
