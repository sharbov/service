# coding: utf-8
from __future__ import absolute_import

import unittest

from tests.ut.base import BaseTestCase


class TestHealth(BaseTestCase):
    """Health endpoint test."""

    def test_health(self):
        """Test get_health."""
        response = self.client.open(
            "/service/api/v1/health",
            method="GET",
            content_type="application/json",
        )
        self.assertStatus(response, 204)


if __name__ == "__main__":
    unittest.main()
