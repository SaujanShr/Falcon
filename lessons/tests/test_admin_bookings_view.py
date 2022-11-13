"""Tests of the admin page to see all bookings and requests."""
from django.test import TestCase

class AdminRequestsViewTestCase(TestCase):
    """Tests of the admin page to see all bookings and requests."""

    def test_get_admin_request_view_page(self):
        url = '/'
