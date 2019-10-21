from unittest import TestCase
from unittest.mock import patch

from django.http import HttpRequest
from django_audit_log.util import get_client_ip


class TestUtil(TestCase):

    def test_get_client_ip_forwarded(self):
        request = HttpRequest()
        request.META['HTTP_X_FORWARDED_FOR'] = '1.2.3.4'
        self.assertEqual(get_client_ip(request), '1.2.3.4')

    def test_get_client_ip(self):
        request = HttpRequest()
        request.META['REMOTE_ADDR'] = '2.3.4.5'
        self.assertEqual(get_client_ip(request), '2.3.4.5')

    @patch('logging.Logger.warning')
    def test_get_client_ip_exception(self, mocked_logger):
        self.assertEqual(get_client_ip(request=None), 'failed to get ip')
        mocked_logger.assert_called_with('Failed to get ip for audit log', exc_info=True)
