# SPDX-FileCopyrightText: 2018-2025 CERN.
# SPDX-License-Identifier: MIT

"""Default configuration for shelfmark.

You overwrite and set instance-specific configuration by either:

- Configuration file: ``<virtualenv prefix>/var/instance/invenio.cfg``
- Environment variables: ``APP_<variable name>``
"""
from datetime import timedelta


def _(x):
    """Identity function used to trigger string extraction."""
    return x


###############################################################################
# Debug
###############################################################################
DEBUG = True
DEBUG_TB_ENABLED = True
DEBUG_TB_INTERCEPT_REDIRECTS = False

###############################################################################
# Rate limiting
###############################################################################
#: Storage for rate limiter.
RATELIMIT_STORAGE_URI = "redis://localhost:6379/3"
#: Rate limit for logged in users.
RATELIMIT_AUTHENTICATED_USER = "5000 per hour;150 per minute"
#: Rate limit for non logged in users.
RATELIMIT_GUEST_USER = "1000 per hour;100 per minute"

###############################################################################
# I18N
###############################################################################
#: Default language
BABEL_DEFAULT_LANGUAGE = "en"
#: Default time zone
BABEL_DEFAULT_TIMEZONE = "Europe/Zurich"
###############################################################################
# Email configuration
###############################################################################
#: Email address for support.
SUPPORT_EMAIL = "info@example.org"
#: Disable email sending by default.
MAIL_SUPPRESS_SEND = True
#: Email address for email notification sender.
MAIL_NOTIFY_SENDER = "noreply@example.org"
#: Email CC address(es) for email notifications.
MAIL_NOTIFY_CC = []
#: Email BCC address(es) for email notification.
MAIL_NOTIFY_BCC = []
# Enable sending mail to test recipients.
ILS_MAIL_ENABLE_TEST_RECIPIENTS = False
#: When ILS_MAIL_ENABLE_TEST_RECIPIENTS=True, all emails are sent here
ILS_MAIL_NOTIFY_TEST_RECIPIENTS = ["onlyme@example.org"]

###############################################################################
# Assets
###############################################################################
#: Static files collection method (defaults to copying files).
COLLECT_STORAGE = "flask_collect.storage.file"

###############################################################################
# Accounts
###############################################################################
#: Email address used as sender of account registration emails.
SECURITY_EMAIL_SENDER = SUPPORT_EMAIL
#: Email subject for account registration emails.
SECURITY_EMAIL_SUBJECT_REGISTER = _("Welcome to Shelfmark!")
#: Redis session storage URL.
ACCOUNTS_SESSION_REDIS_URL = "redis://localhost:6379/1"

###############################################################################
# Celery configuration
###############################################################################
BROKER_URL = "amqp://guest:guest@localhost:5672/"
#: URL of message broker for Celery (default is RabbitMQ).
CELERY_BROKER_URL = "amqp://guest:guest@localhost:5672/"
#: URL of backend for result storage (default is Redis).
CELERY_RESULT_BACKEND = "redis://localhost:6379/2"
#: Scheduled tasks configuration (aka cronjobs).
CELERY_BEAT_SCHEDULE = {
    "indexer": {
        "task": "invenio_indexer.tasks.process_bulk_queue",
        "schedule": timedelta(minutes=5),
    },
    "accounts": {
        "task": "invenio_accounts.tasks.clean_session_table",
        "schedule": timedelta(minutes=60),
    },
}

###############################################################################
# Database
###############################################################################
#: Database URI including user and password
SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://test:psw@localhost/ils"

###############################################################################
# JSONSchemas
###############################################################################
#: Hostname used in URLs for local JSONSchemas.
JSONSCHEMAS_HOST = "127.0.0.1:5000"

###############################################################################
# CSRF
###############################################################################
REST_CSRF_ENABLED = True

###############################################################################
# CORS
###############################################################################
REST_ENABLE_CORS = True
CORS_SEND_WILDCARD = False
CORS_SUPPORTS_CREDENTIALS = True

###############################################################################
# Flask configuration
###############################################################################
# See details on
# http://flask.pocoo.org/docs/0.12/config/#builtin-configuration-values

#: Secret key - each installation (dev, production, ...) needs a separate key.
#: It should be changed before deploying.
SECRET_KEY = "CHANGE_ME"
#: Max upload size for form data via application/mulitpart-formdata.
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100 MiB
#: Sets cookie with the secure flag by default
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = "Lax"
#: Since HAProxy and Nginx route all requests no matter the host header
#: provided, the allowed hosts variable is set to localhost. In production it
#: should be set to the correct host and it is strongly recommended to only
#: route correct hosts to the application.
TRUSTED_HOSTS = ["localhost", "127.0.0.1"]

#: Single Page Application host and routes, useful in templates/emails
SPA_HOST = "https://127.0.0.1:3000"
SPA_PATHS = dict(
    literature="/literature/%(pid)s",
    loan="/backoffice/loans",
    patron="/backoffice/patrons",
    profile="/profile",
    search="/search?q=%(querystring)s",
)
