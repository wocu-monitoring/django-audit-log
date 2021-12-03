from unittest.mock import patch

from django.contrib.auth.models import Group, User
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from django.views import View

from django_audit_log.logger import DjangoAuditLogger


class TestLogger(TestCase):

    def setUp(self):
        self.request_factory = RequestFactory()

    @patch('django_audit_log.app_settings.LOGGER_NAME', 'test_logger_name')
    def test_get_logger_name(self):
        self.assertEqual(DjangoAuditLogger().get_logger_name(), 'test_logger_name')

    def test_get_logger_name_default(self):
        self.assertEqual(DjangoAuditLogger().get_logger_name(), 'audit_log')

    @patch('django_audit_log.logger.AuditLogger.init_logger')
    @patch('django_audit_log.app_settings.LOG_HANDLER_CALLABLE_PATH', 'tests.test_logger.get_log_handler')
    def test_get_log_handler(self, mocked_init_logger):
        self.assertEqual(DjangoAuditLogger().get_log_handler(), get_log_handler())

    @patch('django_audit_log.logger.AuditLogger.get_log_handler')
    def test_get_log_handler_default(self, mocked_get_log_handler):
        DjangoAuditLogger().get_log_handler()
        mocked_get_log_handler.assert_called_with()

    @patch('django_audit_log.app_settings.LOG_FORMATTER_CALLABLE_PATH', 'tests.test_logger.get_log_formatter')
    def test_get_log_formatter(self):
        self.assertEqual(DjangoAuditLogger().get_log_formatter(), get_log_formatter())

    @patch('django_audit_log.logger.AuditLogger.get_log_formatter')
    def test_get_log_formatter_default(self, mocked_get_log_formatter):
        DjangoAuditLogger().get_log_formatter()
        mocked_get_log_formatter.assert_called_with()

    def test_set_django_http_request(self):
        audit_log = DjangoAuditLogger()
        request = self.request_factory.get("/foo/bar?querystr=value",
                                           SERVER_NAME="localhost", HTTP_USER_AGENT='test_agent')
        audit_log.set_django_http_request(request)

        self.assertEqual(audit_log.http_request['method'], 'GET')
        self.assertEqual(audit_log.http_request['url'], 'http://localhost/foo/bar?querystr=value')
        self.assertEqual(audit_log.http_request['user_agent'], 'test_agent')

    def test_set_django_http_response(self):
        audit_log = DjangoAuditLogger()
        request = self.request_factory.get('/')
        response = View.as_view()(request)
        audit_log.set_django_http_response(response)

        self.assertEqual(audit_log.http_response['status_code'], 405)
        self.assertEqual(audit_log.http_response['reason'], 'Method Not Allowed')
        self.assertTrue('Allow' in audit_log.http_response['headers'])
        self.assertTrue('Content-Type' in audit_log.http_response['headers'])

    def test_set_user_from_request(self):
        user = User.objects.create_user(username='username', email='username@host.com')
        group, _ = Group.objects.get_or_create(name='testgroup')
        group.user_set.add(user)

        request = self.request_factory.get("/")
        request.user = user

        audit_log = DjangoAuditLogger()
        audit_log.set_user_from_request(request, realm='testrealm')

        self.assertEqual(audit_log.user['authenticated'], True)
        self.assertEqual(audit_log.user['provider']['name'], '')
        self.assertEqual(audit_log.user['provider']['realm'], 'testrealm')
        self.assertEqual(audit_log.user['email'], 'username@host.com')
        self.assertEqual(audit_log.user['roles'], ['testgroup'])
        self.assertEqual(audit_log.user['ip'], '127.0.0.1')
        self.assertEqual(audit_log.user['username'], 'username')


    def test_extras_user_from_request(self):
        user = User.objects.create_user(username='username', email='username@host.com')
        group, _ = Group.objects.get_or_create(name='testgroup')
        group.user_set.add(user)

        request = self.request_factory.get("/")
        request.user = user

        audit_log = DjangoAuditLogger()
        audit_log.set_user_from_request(request, realm='testrealm')

        extras = audit_log._get_extras(log_type='test')
        self.assertIn('user', extras)
        self.assertEqual(extras['user']['authenticated'], True)
        self.assertEqual(extras['user']['provider']['name'], '')
        self.assertEqual(extras['user']['provider']['realm'], 'testrealm')
        self.assertEqual(extras['user']['email'], 'username@host.com')
        self.assertEqual(extras['user']['roles'], ['testgroup'])
        self.assertEqual(extras['user']['ip'], '127.0.0.1')
        self.assertEqual(extras['user']['username'], 'username')

    def test_get_headers_from_response(self):
        expected_headers = {
            'Header1': 'value1',
            'Header2': 'value2',
            'Header3': 'value3'
        }
        response = HttpResponse()
        for header, value in expected_headers.items():
            response.__setitem__(header, value)

        headers = DjangoAuditLogger()._get_headers_from_response(response)

        # Assert that the header we put in, will come out.
        # Note that the HttpResponse class will add a default header
        # 'content-type'.
        for header, expected_value in expected_headers.items():
            self.assertEqual(headers[header], expected_value)


def get_log_handler():
    return 'test_handler'


def get_log_formatter():
    return 'test_formatter'
