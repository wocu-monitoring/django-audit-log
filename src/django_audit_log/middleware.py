import re

from django.http import HttpRequest, HttpResponse
from django.utils.deprecation import MiddlewareMixin

from django_audit_log import app_settings
from django_audit_log.logger import DjangoAuditLogger


class AuditLogMiddleware(MiddlewareMixin):
    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.redirect_exempt = [re.compile(r) for r in app_settings.EXEMPT_URLS]

    def process_request(self, request: HttpRequest) -> None:
        if not hasattr(request, 'audit_log') and not self.exempt_request(request):
            audit_log = DjangoAuditLogger()
            audit_log.set_django_http_request(request)
            audit_log.set_user_from_request(request)
            request.audit_log = audit_log

    def process_response(
        self, request: HttpRequest, response: HttpResponse
    ) -> HttpResponse:
        if hasattr(request, 'audit_log'):
            audit_log = request.audit_log
            audit_log.set_django_http_response(response)
            audit_log.send_log()
        return response

    def exempt_request(self, request):
        path = request.path.lstrip("/")
        return any(pattern.search(path) for pattern in self.redirect_exempt)
