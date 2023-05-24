# SPDX-FileCopyrightText: 2018-2025 CERN.
# SPDX-License-Identifier: MIT

"""Default configuration for shelfmark.

You overwrite and set instance-specific configuration by either:

- Configuration file: ``<virtualenv prefix>/var/instance/invenio.cfg``
- Environment variables: ``APP_<variable name>``
"""
from datetime import timedelta
from invenio_accounts.config import (
    ACCOUNTS_REST_AUTH_VIEWS as _ACCOUNTS_REST_AUTH_VIEWS,
)
from invenio_records_rest.utils import allow_all, deny_all
from shelfmark.vocabularies.indexer import VocabularyIndexer
from .views import UserInfoResource
from .vocabularies.api import (
    VOCABULARY_PID_FETCHER,
    VOCABULARY_PID_MINTER,
    VOCABULARY_PID_TYPE,
    Vocabulary,
)
from .vocabularies.search import VocabularySearch


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

_ACCOUNTS_REST_AUTH_VIEWS.update(user_info=UserInfoResource)
ACCOUNTS_REST_AUTH_VIEWS = _ACCOUNTS_REST_AUTH_VIEWS

ACCOUNTS_REST_CONFIRM_EMAIL_ENDPOINT = "/accounts/confirm-email"

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

RECORDS_REST_MAX_RESULT_WINDOW = 10000
RECORDS_REST_VOCAB_MAX_RESULT_WINDOW = 500
PIDSTORE_RECID_FIELD = "pid"
# name of the URL arg to choose response serializer
REST_MIMETYPE_QUERY_ARG_NAME = "format"

RECORDS_REST_ENDPOINTS = dict(
    vocid=dict(
        pid_type=VOCABULARY_PID_TYPE,
        pid_minter=VOCABULARY_PID_MINTER,
        pid_fetcher=VOCABULARY_PID_FETCHER,
        search_class=VocabularySearch,
        indexer_class=VocabularyIndexer,
        record_class=Vocabulary,
        record_serializers={
            "application/json": "shelfmark.records.serializers:json_v1_response"
        },
        search_serializers={
            "application/json": "shelfmark.records.serializers:json_v1_search",
            "text/csv": "shelfmark.records.serializers:csv_v1_search",
        },
        search_serializers_aliases={
            "csv": "text/csv",
            "json": "application/json",
        },
        item_route="/vocabularies/<pid({}):pid_value>".format(VOCABULARY_PID_TYPE),
        list_route="/vocabularies/",
        default_media_type="application/json",
        max_result_window=RECORDS_REST_VOCAB_MAX_RESULT_WINDOW,
        error_handlers=dict(),
        read_permission_factory_imp=deny_all,
        list_permission_factory_imp=allow_all,
        create_permission_factory_imp=deny_all,
        update_permission_factory_imp=deny_all,
        delete_permission_factory_imp=deny_all,
    ),
)

# List of available vocabularies
ILS_VOCABULARIES = [
    "acq_medium",
    "acq_order_line_payment_mode",
    "acq_order_line_purchase_type",
    "acq_payment_mode",
    "acq_recipient",
    "affiliation_identifier_scheme",
    "alternative_identifier_scheme",
    "alternative_title_type",
    "author_identifier_scheme",
    "author_role",
    "author_type",
    "conference_identifier_scheme",
    "country",
    "currencies",
    "doc_req_type",
    "doc_req_payment_method",
    "doc_identifiers_materials",
    "doc_req_medium",
    "doc_subjects",
    "eitem_sources",
    "identifier_scheme",
    "ill_item_type",
    "ill_payment_mode",
    "item_medium",
    "language",
    "license",
    "provider_type",
    "series_identifier_scheme",
    "series_url_access_restriction",
    "tag",
]

ILS_VOCABULARY_SOURCES = {
    "json": "shelfmark.vocabularies.sources:json_source",
    "opendefinition": (
        "shelfmark.vocabularies.sources:opendefinition_source"
    ),  # noqa
}

OPENDEFINITION_JSONRESOLVER_HOST = "inveniosoftware.org"

# Use default frontpage
THEME_FRONTPAGE = False

# Default template to render.
PAGES_DEFAULT_TEMPLATE = "invenio_pages/default.html"
# default app theme
APP_THEME = ["semantic-ui"]

# Site name.
THEME_SITENAME = _("Shelfmark")
