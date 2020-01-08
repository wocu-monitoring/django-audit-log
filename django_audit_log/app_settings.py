
from django.conf import settings

# Internal logger name used by the audit log. Leave None to use python-audit-log default ('audit_log')
LOGGER_NAME = getattr(settings, 'AUDIT_LOG_LOGGER_NAME', None)

# Log handler that determines what to do with the logs. Leave None to use python-audit-log default (write to stdout)
LOG_HANDLER_CALLABLE_PATH = getattr(settings, 'AUDIT_LOG_HANDLER_CALLABLE_PATH', None)

# Log formatter that determines log formatting. Leave None to use python-audit-log default (AuditLogFormatter)
LOG_FORMATTER_CALLABLE_PATH = getattr(settings, 'AUDIT_LOG_FORMATTER_CALLABLE_PATH', None)
