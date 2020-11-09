from django.conf import settings

# Internal logger name used by the audit log. Leave None to use python-audit-log default ('audit_log')
LOGGER_NAME = getattr(settings, 'AUDIT_LOG_LOGGER_NAME', None)

# Log handler that determines what to do with the logs. Leave None to use python-audit-log default (write to stdout)
LOG_HANDLER_CALLABLE_PATH = getattr(settings, 'AUDIT_LOG_HANDLER_CALLABLE_PATH', None)

# Log formatter that determines log formatting. Leave None to use python-audit-log default (AuditLogFormatter)
LOG_FORMATTER_CALLABLE_PATH = getattr(
    settings, 'AUDIT_LOG_FORMATTER_CALLABLE_PATH', None
)

# List of url names that will not be logged (e.g. health urls)
# Default: [] (Empty list)

# If a URL path matches a regular expression in this list, the request will not be redirected to HTTPS.
# The AuditLogMiddleware strips leading slashes from URL paths, so patterns shouldn’t include them, e.g.
# AUDIT_LOG_EXEMPT_URLS = [r'^foo/bar/$', …].
EXEMPT_URLS = getattr(settings, 'AUDIT_LOG_EXEMPT_URLS', [])

assert type(EXEMPT_URLS) is list, "EXEMPT_URLS must be a list"
