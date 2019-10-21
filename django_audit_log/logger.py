from audit_log.logger import AuditLogger

from django.http import HttpRequest, HttpResponse
from django_audit_log.util import get_client_ip


class DjangoAuditLogger(AuditLogger):

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
