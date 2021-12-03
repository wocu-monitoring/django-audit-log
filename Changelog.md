
## [unreleased - 03-01-2021]
- Allow `username` logging when user is authenticated
## 0.4.0 (29-01-2020)

### Note worthy changes
- Implemented AUDIT_LOG_EXEMPT_URLS to allow certain urls to be ignored by the audit logger

### Backwards incompatible changes
- None


## 0.3.0 (08-01-2020)

### Note worthy changes
- Allow to set log handler, formatter and name in settings

### Backwards incompatible changes
- None


## 0.2.0 (31-10-2019)

### Note worthy changes
- Replaced f-strings with %-formatting (#5)
- Fixed malfunctioning release make target (#4)
- Improved prepare release makefile
- Implemented django rest framework base viewsets (#2)
- Implemented prepare_release.sh (#3)

### Backwards incompatible changes
- AuditLogger.filter() signature changed to filter(object_name: str, kwargs: dict). 
See https://github.com/Amsterdam/python-audit-log/commit/8a4daf8a04d55cc9adc7c5283b3633fc4ef43b2f


## 0.1.1 (28-10-2019)

### Note worthy changes
- README update
- Removed outdated dependency in tox.ini

### Backwards incompatible changes
- None


## 0.1.0 (28-10-2019)

### Note worthy changes
- Initial release.

### Backwards incompatible changes
- None 
