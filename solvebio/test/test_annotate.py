# -*- coding: utf-8 -*-
from __future__ import absolute_import

from .helper import SolveBioTestCase


class TestAnnotator(SolveBioTestCase):

    def test_annotator(self):
        fields = [{'name': 'test', 'expression': '"hello world"'}]
        records = [{'i': i} for i in range(100)]
        a = self.client.Annotator(fields)

        for i, result in enumerate(a.annotate(records)):
            self.assertEqual(
                result, {'test': 'hello world', 'i': i})


class TestExpression(SolveBioTestCase):

    def test_expression(self):
        answer = self.client.Expression("1+1").evaluate(data_type="integer")
        self.assertEqual(answer, 2)

    def test_expression_with_context(self):
        answer = self.client.Expression("record").evaluate(
            data={'record': 123}, data_type="integer")
        self.assertEqual(answer, 123)
