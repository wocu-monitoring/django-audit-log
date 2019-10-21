from django.http import HttpRequest, HttpResponse
from django.utils.deprecation import MiddlewareMixin

from django_audit_log.logger import DjangoAuditLogger


class AuditLogMiddleware(MiddlewareMixin):

    def process_request(self, request: HttpRequest) -> None:
        if not hasattr(request, 'audit_log'):
            audit_log = DjangoAuditLogger()
            audit_log.set_django_http_request(request)
            audit_log.set_user_from_request(request)
            request.audit_log = audit_log

    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        if hasattr(request, 'audit_log'):
            audit_log = request.audit_log
            audit_log.set_django_http_response(response)
            audit_log.send_log()
        return response
