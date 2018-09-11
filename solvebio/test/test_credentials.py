# -*- coding: utf-8 -*-
from __future__ import absolute_import

import os
import shutil
import sys
import unittest
import solvebio
import solvebio.cli.credentials as creds
import contextlib


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


class TestCredentials(unittest.TestCase):
    def setUp(self):
        self.solvebiodir = os.path.join(os.path.dirname(__file__),
                                        'data', '.solvebio')
        self.api_host = solvebio.api_host
        solvebio.api_host = 'https://api.solvebio.com'

    def tearDown(self):
        solvebio.api_host = self.api_host
        if os.path.isdir(self.solvebiodir):
            shutil.rmtree(self.solvebiodir)

    def test_credentials(self):

        datadir = os.path.join(os.path.dirname(__file__), 'data')
        os.environ['HOME'] = datadir

        # Make sure we don't have have the test solvebio directory
        if os.path.isdir(self.solvebiodir):
            shutil.rmtree(self.solvebiodir)

        cred_file = creds.netrc.path()
        self.assertTrue(os.path.exists(cred_file),
                        "cred file created when it doesn't exist first")

        self.assertEqual(creds.get_credentials(), None,
                         'Should not find credentials')

        test_credentials_file = os.path.join(datadir, 'test_creds')
        shutil.copy(test_credentials_file, cred_file)

        auths = creds.get_credentials()
        self.assertTrue(auths is not None, 'Should find credentials')

        solvebio.api_host = 'https://example.com'

        auths = creds.get_credentials()
        self.assertEqual(auths, None,
                         'Should not find credentials for host {0}'
                         .format(solvebio.api_host))

        solvebio.api_host = 'https://api.solvebio.com'
        creds.delete_credentials()
        auths = creds.get_credentials()
        self.assertEqual(auths, None,
                         'Should not find removed credentials for '
                         'host {0}'.format(solvebio.api_host))

        pair = ('testagain@solvebio.com', 'b00b00',)
        creds.save_credentials(*pair)
        auths = creds.get_credentials()
        self.assertTrue(auths is not None,
                        'Should get newly set credentials for '
                        'host {0}'.format(solvebio.api_host))

        self.assertEqual(auths, pair[1], 'Should get back creds we saved')
