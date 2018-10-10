# -*- coding: utf-8 -*-
from __future__ import absolute_import

import time
from mock import patch

import solvebio.client
from .helper import SolveBioTestCase


class FakeResponse():
    def __init__(self, headers, status_code):
        self.headers = headers
        self.status_code = status_code

    def json(self):
        return {}


class ClientRateLimit(SolveBioTestCase):
    """Test of rate-limiting an API request"""

    def setUp(self):
        super(ClientRateLimit, self).setUp()
        self.call_count = 0

    def fake_response(self):
        if self.call_count == 0:
            self.call_count += 1
            return FakeResponse({'retry-after': '0'}, 429)
        else:
            return FakeResponse({}, 200)

    def test_rate_limit(self):
        with patch('solvebio.client.Session.request') as mock_request:
            mock_request.side_effect = lambda *args, **kw: self.fake_response()
            start_time = time.time()
            dataset = solvebio.Dataset.retrieve(1)
            elapsed_time = time.time() - start_time
            self.assertTrue(isinstance(dataset, solvebio.Dataset),
                            "Got a dataset back (eventually)")
            self.assertTrue(elapsed_time > 1.0,
                               "Should have delayed for over a second; "
                               "(was %s)" % elapsed_time)
            self.assertEqual(self.call_count, 1)
