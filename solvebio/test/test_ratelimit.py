#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import mock
import solvebio.client
import time


class FakeResponse():
    """
    Mock some fake requests reponses to given back to client.py's
    request method to cause it to retry.
    """
    def __init__(self, tst_cls):
        self.next_status_code = 429
        self.status_code = 429
        self.tst_cls = tst_cls

    def json(self):
        self.status_code = self.next_status_code
        if self.status_code == 429:
            self.tst_cls.assertTrue(True, "Gave back a 429 response")
            self.next_status_code = 200
            # Note: the detail message should to match exactly the
            # message we would get back from api.solvebio.com with some
            # sort of time in it in seconds.
            return {'detail':
                    'Request was throttled. Expected available in 1 seconds.'
                    }
        else:
            self.tst_cls.assertEqual(self.status_code, 200,
                                     "Gave back normal response")
            return {}


class ClientRateLimit(unittest.TestCase):
    """Test of rate-limiting an API request"""
    @mock.patch('solvebio.client.requests')
    def test_rate_limit(self, mock_client_requests):
        mock_client_requests.request.return_value = FakeResponse(self)
        start_time = time.time()
        depo = solvebio.Depository.retrieve('ClinVar')
        self.assertTrue(isinstance(depo, solvebio.Depository),
                                   "Got a depository back (eventually)")
        elapsed_time = time.time() - start_time
        self.assertGreater(elapsed_time, 1.0,
                           "Should have delayed for over a second; (was %s)" %
                           elapsed_time)
