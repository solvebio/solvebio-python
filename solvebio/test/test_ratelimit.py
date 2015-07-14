# -*- coding: utf-8 -*-
from __future__ import absolute_import

import unittest
from mock import patch
import solvebio.client
import time


class FakeResponse():
    def __init__(self, headers, status_code):
        self.headers = headers
        self.status_code = status_code

    def json(self):
        return {}


class ClientRateLimit(unittest.TestCase):
    """Test of rate-limiting an API request"""

    def setUp(self):
        self.call_count = 0

    def fake_response(self):
        if self.call_count == 0:
            self.call_count += 1
            return FakeResponse({'retry-after': '0'}, 429)
        else:
            return FakeResponse({}, 200)

    def test_rate_limit(self):
        with patch('solvebio.client.requests.request') as mock_request:
            mock_request.side_effect = lambda *args, **kw: self.fake_response()
            start_time = time.time()
            depo = solvebio.Depository.retrieve('HGNC')
            elapsed_time = time.time() - start_time
            self.assertTrue(isinstance(depo, solvebio.Depository),
                            "Got a depository back (eventually)")
            self.assertTrue(elapsed_time > 1.0,
                               "Should have delayed for over a second; "
                               "(was %s)" % elapsed_time)
            self.assertEqual(self.call_count, 1)
