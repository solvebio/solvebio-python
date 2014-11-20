# -*- coding: utf-8 -*-
import contextlib
import sys
import unittest
import solvebio
import solvebio.cli.auth as auth
import mock


@contextlib.contextmanager
def nostdout():
    savestderr = sys.stdout

    class Devnull(object):
        def write(self, _):
            pass
    sys.stdout = Devnull()
    try:
        yield
    finally:
        sys.stdout = savestderr


class TestLogin(unittest.TestCase):
    def setUp(self):
        self.api_host = solvebio.api_host
        # temporarily replace with dummy methods for testing
        self._ask_for_credentials = auth._ask_for_credentials
        self.delete_credentials = auth.delete_credentials
        auth._ask_for_credentials = lambda login=None: ('fake@foo.bar',
                                                        'p4ssw0rd')
        auth.delete_credentials = lambda: None

    def tearDown(self):
        solvebio.api_host = self.api_host
        auth._ask_for_credentials = self._ask_for_credentials
        auth.delete_credentials = self.delete_credentials

    def test_bad_login(self):
        with nostdout():
            self.assertEqual(auth.login('foo'), False, 'Invalid login')

            # Test invalid host
            solvebio.api_host = 'https://some.fake.domain.foobar'
            self.assertEqual(auth.login('foo'), False,
                             "Invalid login")

    @mock.patch('solvebio.cli.auth.save_credentials')
    def test_api_key_login(self, mock_auth):
        mock_auth.save_credentials.return_value = None
        with nostdout():
            api_key = '0cedb161d845e6a58ec6781478b8314c536e632f'
            self.assertTrue(auth.login(email=None,
                                       api_key=api_key))

            calls = mock_auth.mock_calls
            self.assertEqual(len(calls), 1)
            self.assertTrue(calls[0][1][0].endswith('@solvebio.com'))
            self.assertEqual(calls[0][1][1], api_key)
