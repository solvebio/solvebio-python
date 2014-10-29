# -*- coding: utf-8 -*-
import solvebio
import solvebio.cli.auth as auth

from .helper import unittest


class TestLogin(unittest.TestCase):
    def setUp(self):
        self.api_host = solvebio.api_host
        self._ask_for_credentials = auth._ask_for_credentials
        self.delete_credentials = auth.delete_credentials

        auth._ask_for_credentials = lambda: ('fake@foo.bar', 'p4ssw0rd')
        auth.delete_credentials = lambda: None

    def tearDown(self):
        solvebio.api_host = self.api_host
        auth._ask_for_credentials = self._ask_for_credentials
        auth.delete_credentials = self.delete_credentials

    def test_bad_login(self):
        self.assertEqual(auth.login('foo'), False, "Invalid login")

        # Test invalid host
        solvebio.api_host = 'https://some.fake.domain.foobar'
        self.assertEqual(auth.login('foo'), False,
                         "Invalid login")