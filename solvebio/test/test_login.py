#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
import solvebio
import solvebio.cli.auth as Mauth


def bad_creds():
    return 'rocky@foo.bar', 'weird'


def fake_delete_credentials():
    return


class TestLogin(unittest.TestCase):

    def setUp(self):
        self.api_host_save = solvebio.api_host

    def tearDown(self):
        solvebio.api_host = self.api_host_save

    def test_bad_login(self):
        Mauth._ask_for_credentials = bad_creds
        Mauth.delete_credentials = fake_delete_credentials
        self.assertEqual(Mauth.login('foo'), False, "Invalid login")
        solvebio.api_host = 'https://stagfoo.bar'
        self.assertEqual(Mauth.login('foo'), False,
                         "Invalid login")
        solvebio.api_host = self.api_host_save


if __name__ == "__main__":
    unittest.main()
