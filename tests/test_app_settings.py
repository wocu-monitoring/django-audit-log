from django.test import TestCase
from django_audit_log import app_settings


class TestAppSettings(TestCase):

    def test_valid_settings(self):
        self.assertEqual(app_settings.AUDIT_LOG_APP_NAME, 'test', 'AUDIT_LOG_APP_NAME has unexpected value')

    def test_missing_app_name(self):
        pass
        # TODO implement
        # with mock.patch('django_audit_log.app_settings.AUDIT_LOG_APP_NAME', None):
        #     with self.assertRaises(ImproperlyConfigured):
        #         from django_audit_log import app_settings
