from unittest.mock import patch

from audit_log.logger import AuditLogger
from django.test import RequestFactory, TestCase
from django.views import View

from django_audit_log.middleware import AuditLogMiddleware


class TestMiddleware(TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.request_factory = RequestFactory()
        self.middleware = AuditLogMiddleware()

    def test_process_request_attribute(self):
        """
        Assert that the middleware attaches the audit log to the request.
        """
        request = self.request_factory.get('/')
        self.middleware.process_request(request)

        # assert that the auditlog attribute has been added to the request
        self.assertTrue(hasattr(request, 'audit_log'),
                        "Request should have audit_log attribute after passing through middleware")
        self.assertTrue(isinstance(request.audit_log, AuditLogger))

    def test_process_request_already_attached(self):
        """
        Assert that the middleware does not attach the audit log again if attribute already exists
        """
        request = self.request_factory.get('/')
        request.audit_log = 'test'
        self.middleware.process_request(request)

        self.assertEqual(request.audit_log, 'test', "Expected request.audit_log to not have been modified "
                                                    "because request.audit_log was already present")

    @patch('django_audit_log.middleware.DjangoAuditLogger')
    def test_process_request_extras(self, mocked_auditlog):
        """
        Assert that the middleware calls the proper methods to add extras
        to the audit log.
        """
        request = self.request_factory.get('/')
        self.middleware.process_request(request)

        mocked_instance = mocked_auditlog.return_value
        mocked_instance.set_django_http_request.assert_called_with(request)
        mocked_instance.set_user_from_request.assert_called_with(request)

    @patch('django_audit_log.middleware.DjangoAuditLogger')
    def test_process_response(self, mocked_auditlog):
        """
        Assert that the response has been added to the audit log and
        that the log has been fired.
        """
        # prepare request
        request = self.request_factory.get('/')
        self.middleware.process_request(request)

        # prepare response
        response = View.as_view()(request)
        self.middleware.process_response(request, response)

        mocked_instance = mocked_auditlog.return_value
        mocked_instance.set_django_http_response.assert_called_with(response)
        mocked_instance.send_log.assert_called()

    @patch('django_audit_log.middleware.DjangoAuditLogger')
    def test_process_response_without_auditlog(self, mocked_auditlog):
        """
        Assert that when the audit log does not exist, we do not try to call any
        methods on it
        """
        # prepare request (but don't pass through middleware, so that hasattr(request, 'audit_log') is False
        request = self.request_factory.get('/')
        self.assertFalse(hasattr(request, 'audit_log'), "Audit log should not have been attached to request")

        # prepare response
        response = View.as_view()(request)
        self.middleware.process_response(request, response)

        mocked_instance = mocked_auditlog.return_value
        mocked_instance.set_http_response.assert_not_called()
        mocked_instance.send_log.assert_not_called()
