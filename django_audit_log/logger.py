import logging

from django.http import HttpRequest, HttpResponse

from audit_log.logger import AuditLogger
from django_audit_log import app_settings
from django_audit_log.util import get_client_ip, import_callable


class DjangoAuditLogger(AuditLogger):

    def get_logger_name(self) -> str:
        logger_name = app_settings.LOGGER_NAME
        if not logger_name:
            return super().get_logger_name()
        return logger_name

    def get_log_handler(self) -> logging.Handler:
        log_handler_path = app_settings.LOG_HANDLER_CALLABLE_PATH
        if not log_handler_path:
            return super().get_log_handler()

        log_handler_callable = import_callable(log_handler_path)
        return log_handler_callable()

    def get_log_formatter(self) -> logging.Formatter:
        log_formatter_path = app_settings.LOG_FORMATTER_CALLABLE_PATH
        if not log_formatter_path:
            return super().get_log_formatter()

        log_formatter_callable = import_callable(log_formatter_path)
        return log_formatter_callable()

    def set_django_http_request(self, request: HttpRequest) -> 'DjangoAuditLogger':
        self.set_http_request(
            method=request.method,
            url=request.build_absolute_uri(),
            user_agent=request.META.get('HTTP_USER_AGENT', '?') if request.META else '?'
        )
        return self

    def set_django_http_response(self, response: HttpResponse) -> 'DjangoAuditLogger':
        headers = self._get_headers_from_response(response)
        self.set_http_response(
            status_code=getattr(response, 'status_code', ''),
            reason=getattr(response, 'reason_phrase', ''),
            headers=headers
        )
        return self

    def set_user_from_request(self, request: HttpRequest, realm='') -> 'DjangoAuditLogger':
        user = request.user if hasattr(request, 'user') else None
        roles = list(user.groups.values_list('name', flat=True)) if user else []
        self.set_user(
            authenticated=user.is_authenticated if user else False,
            provider=request.session.get('_auth_user_backend', '') if hasattr(request, 'session') else '',
            realm=realm,
            email=getattr(user, 'email', '') if user else '',
            roles=roles,
            ip=get_client_ip(request)
        )
        return self

    def _get_headers_from_response(self, response: HttpResponse) -> dict:
        return {header: value for header, value in response.items()}
