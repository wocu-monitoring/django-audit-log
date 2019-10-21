from django.contrib.auth.models import Group, User
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from django.views import View

from django_audit_log.logger import DjangoAuditLogger


class TestLogger(TestCase):

    def setUp(self):
        self.request_factory = RequestFactory()

    def test_set_django_http_request(self):
        auditlog = DjangoAuditLogger()
        request = self.request_factory.get("/",  SERVER_NAME="localhost", HTTP_USER_AGENT='test_agent')
        auditlog.set_django_http_request(request)

        self.assertEqual(auditlog.http_request['method'], 'GET')
        self.assertEqual(auditlog.http_request['url'], 'http://localhost/')
        self.assertEqual(auditlog.http_request['user_agent'], 'test_agent')

    def test_set_django_http_response(self):
        auditlog = DjangoAuditLogger()
        request = self.request_factory.get('/')
        response = View.as_view()(request)
        auditlog.set_django_http_response(response)

        self.assertEqual(auditlog.http_response['status_code'], 405)
        self.assertEqual(auditlog.http_response['reason'], 'Method Not Allowed')
        self.assertTrue('Allow' in auditlog.http_response['headers'])
        self.assertTrue('Content-Type' in auditlog.http_response['headers'])

    def test_set_user_from_request(self):
        user = User.objects.create_user(username='username', email='username@host.com')
        group, _ = Group.objects.get_or_create(name='testgroup')
        group.user_set.add(user)

        request = self.request_factory.get("/")
        request.user = user

        auditlog = DjangoAuditLogger()
        auditlog.set_user_from_request(request, realm='testrealm')

        self.assertEqual(auditlog.user['authenticated'], True)
        self.assertEqual(auditlog.user['provider']['name'], '')
        self.assertEqual(auditlog.user['provider']['realm'], 'testrealm')
        self.assertEqual(auditlog.user['email'], 'username@host.com')
        self.assertEqual(auditlog.user['roles'], ['testgroup'])
        self.assertEqual(auditlog.user['ip'], '127.0.0.1')

    def test_extras_user_from_request(self):
        user = User.objects.create_user(username='username', email='username@host.com')
        group, _ = Group.objects.get_or_create(name='testgroup')
        group.user_set.add(user)

        request = self.request_factory.get("/")
        request.user = user

        auditlog = DjangoAuditLogger()
        auditlog.set_user_from_request(request, realm='testrealm')

        extras = auditlog._get_extras(log_type='test')
        self.assertIn('user', extras)
        self.assertEqual(extras['user']['authenticated'], True)
        self.assertEqual(extras['user']['provider']['name'], '')
        self.assertEqual(extras['user']['provider']['realm'], 'testrealm')
        self.assertEqual(extras['user']['email'], 'username@host.com')
        self.assertEqual(extras['user']['roles'], ['testgroup'])
        self.assertEqual(extras['user']['ip'], '127.0.0.1')

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
