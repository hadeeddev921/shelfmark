# SPDX-FileCopyrightText: 2018-2025 CERN.
# SPDX-License-Identifier: MIT

"""Default configuration for shelfmark.

You overwrite and set instance-specific configuration by either:

- Configuration file: ``<virtualenv prefix>/var/instance/invenio.cfg``
- Environment variables: ``APP_<variable name>``
"""
from datetime import timedelta

from celery.schedules import crontab
from invenio_accounts.config import (
    ACCOUNTS_REST_AUTH_VIEWS as _ACCOUNTS_REST_AUTH_VIEWS,
)
from invenio_records_rest.facets import terms_filter
from invenio_records_rest.utils import allow_all, deny_all
from shelfmark.eitems.indexer import EItemIndexer
from shelfmark.internal_locations.indexer import InternalLocationIndexer
from shelfmark.items.indexer import ItemIndexer
from shelfmark.literature.api import (
    LITERATURE_PID_FETCHER,
    LITERATURE_PID_MINTER,
    LITERATURE_PID_TYPE,
)
from shelfmark.literature.search import LiteratureSearch
from shelfmark.locations.indexer import LocationIndexer
from shelfmark.series.indexer import SeriesIndexer
from shelfmark.vocabularies.indexer import VocabularyIndexer
from .eitems.api import EITEM_PID_FETCHER, EITEM_PID_MINTER, EITEM_PID_TYPE, EItem
from .eitems.search import EItemSearch
from .facets import default_value_when_missing_filter, exists_value_filter
from .internal_locations.api import (
    INTERNAL_LOCATION_PID_FETCHER,
    INTERNAL_LOCATION_PID_MINTER,
    INTERNAL_LOCATION_PID_TYPE,
    InternalLocation,
)
from .internal_locations.search import InternalLocationSearch
from .items.api import ITEM_PID_FETCHER, ITEM_PID_MINTER, ITEM_PID_TYPE, Item
from .items.search import ItemSearch
from .locations.api import (
    LOCATION_PID_FETCHER,
    LOCATION_PID_MINTER,
    LOCATION_PID_TYPE,
    Location,
)
from .locations.search import LocationSearch
from .permissions import backoffice_permission, backoffice_read_permission
from .records.permissions import record_read_permission_factory
from .series.api import SERIES_PID_FETCHER, SERIES_PID_MINTER, SERIES_PID_TYPE, Series
from .series.search import SeriesSearch
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
    "send_expiring_loans_loans": {
        "task": "shelfmark.circulation.notifications.tasks.send_expiring_loans_notification_reminder",  # noqa
        "schedule": crontab(minute=0, hour=0),  # every day, midnight
    },
    "cancel_expired_loan": {
        "task": (
            "shelfmark.circulation.tasks.cancel_expired_loan_requests"
        ),  # noqa
        "schedule": crontab(minute=0, hour=1),  # every day, 1am
    },
    "send_overdue_loan_reminders": {
        "task": "shelfmark.circulation.notifications.tasks.send_overdue_loans_notification_reminder",  # noqa
        "schedule": crontab(minute=0, hour=2),  # every day, 2am
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
_PITMID_CONVERTER = 'pid(pitmid, record_class="shelfmark.items.api:Item")'
_EITMID_CONVERTER = 'pid(eitmid, record_class="shelfmark.eitems.api:EItem")'
_LOCID_CONVERTER = 'pid(locid, record_class="shelfmark.locations.api:Location")'
_ILOCID_CONVERTER = 'pid(ilocid, record_class="shelfmark.internal_locations.api:InternalLocation")'  # noqa
_SERID_CONVERTER = 'pid(serid, record_class="shelfmark.series.api:Series")'

RECORDS_REST_MAX_RESULT_WINDOW = 10000
RECORDS_REST_VOCAB_MAX_RESULT_WINDOW = 500
PIDSTORE_RECID_FIELD = "pid"
# name of the URL arg to choose response serializer
REST_MIMETYPE_QUERY_ARG_NAME = "format"

RECORDS_REST_ENDPOINTS = dict(
    pitmid=dict(
        pid_type=ITEM_PID_TYPE,
        pid_minter=ITEM_PID_MINTER,
        pid_fetcher=ITEM_PID_FETCHER,
        search_class=ItemSearch,
        record_class=Item,
        indexer_class=ItemIndexer,
        record_loaders={
            "application/json": "shelfmark.items.loaders:item_loader"
        },
        record_serializers={
            "application/json": "shelfmark.items.serializers:json_v1_response"
        },
        search_serializers={
            "application/json": "shelfmark.items.serializers:json_v1_search",
            "text/csv": "shelfmark.items.serializers:csv_v1_search",
        },
        search_serializers_aliases={
            "csv": "text/csv",
            "json": "application/json",
        },
        list_route="/items/",
        item_route="/items/<{0}:pid_value>".format(_PITMID_CONVERTER),
        default_media_type="application/json",
        max_result_window=RECORDS_REST_MAX_RESULT_WINDOW,
        error_handlers=dict(),
        read_permission_factory_imp=backoffice_read_permission,
        list_permission_factory_imp=backoffice_read_permission,
        create_permission_factory_imp=backoffice_permission,
        update_permission_factory_imp=backoffice_permission,
        delete_permission_factory_imp=backoffice_permission,
    ),
    eitmid=dict(
        pid_type=EITEM_PID_TYPE,
        pid_minter=EITEM_PID_MINTER,
        pid_fetcher=EITEM_PID_FETCHER,
        search_class=EItemSearch,
        record_class=EItem,
        indexer_class=EItemIndexer,
        record_loaders={
            "application/json": "shelfmark.eitems.loaders:eitem_loader"
        },
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
        list_route="/eitems/",
        item_route="/eitems/<{0}:pid_value>".format(_EITMID_CONVERTER),
        default_media_type="application/json",
        max_result_window=RECORDS_REST_MAX_RESULT_WINDOW,
        error_handlers=dict(),
        read_permission_factory_imp=backoffice_read_permission,
        list_permission_factory_imp=backoffice_read_permission,
        create_permission_factory_imp=backoffice_permission,
        update_permission_factory_imp=backoffice_permission,
        delete_permission_factory_imp=backoffice_permission,
    ),
    locid=dict(
        pid_type=LOCATION_PID_TYPE,
        pid_minter=LOCATION_PID_MINTER,
        pid_fetcher=LOCATION_PID_FETCHER,
        search_class=LocationSearch,
        record_class=Location,
        indexer_class=LocationIndexer,
        record_loaders={
            "application/json": "shelfmark.locations.loaders:location_loader"
        },
        record_serializers={
            "application/json": "shelfmark.records.serializers:json_v1_response"
        },
        search_serializers={
            "application/json": "shelfmark.records.serializers:json_v1_search"
        },
        search_serializers_aliases={
            "json": "application/json",
        },
        list_route="/locations/",
        item_route="/locations/<{0}:pid_value>".format(_LOCID_CONVERTER),
        default_media_type="application/json",
        max_result_window=RECORDS_REST_MAX_RESULT_WINDOW,
        error_handlers=dict(),
        read_permission_factory_imp=record_read_permission_factory,
        list_permission_factory_imp=allow_all,
        create_permission_factory_imp=backoffice_permission,
        update_permission_factory_imp=backoffice_permission,
        delete_permission_factory_imp=backoffice_permission,
    ),
    serid=dict(
        pid_type=SERIES_PID_TYPE,
        pid_minter=SERIES_PID_MINTER,
        pid_fetcher=SERIES_PID_FETCHER,
        search_class=SeriesSearch,
        record_class=Series,
        indexer_class=SeriesIndexer,
        search_factory_imp="shelfmark.search_permissions:ils_search_factory",  # noqa
        record_loaders={
            "application/json": "shelfmark.series.loaders:series_loader"
        },
        record_serializers={
            "application/json": (
                "shelfmark.literature.serializers:json_v1_response"
            )
        },
        search_serializers={
            "application/json": "shelfmark.literature.serializers:json_v1_search",
            "text/csv": "shelfmark.literature.serializers:csv_v1_search",
        },
        search_serializers_aliases={
            "csv": "text/csv",
            "json": "application/json",
        },
        list_route="/series/",
        item_route="/series/<{0}:pid_value>".format(_SERID_CONVERTER),
        default_media_type="application/json",
        max_result_window=RECORDS_REST_MAX_RESULT_WINDOW,
        error_handlers=dict(),
        read_permission_factory_imp=record_read_permission_factory,
        list_permission_factory_imp=allow_all,
        create_permission_factory_imp=backoffice_permission,
        update_permission_factory_imp=backoffice_permission,
        delete_permission_factory_imp=backoffice_permission,
    ),
    ilocid=dict(
        pid_type=INTERNAL_LOCATION_PID_TYPE,
        pid_minter=INTERNAL_LOCATION_PID_MINTER,
        pid_fetcher=INTERNAL_LOCATION_PID_FETCHER,
        search_class=InternalLocationSearch,
        record_class=InternalLocation,
        indexer_class=InternalLocationIndexer,
        record_loaders={
            "application/json": "shelfmark.internal_locations.loaders:internal_location_loader"  # noqa
        },
        record_serializers={
            "application/json": "shelfmark.records.serializers:json_v1_response"
        },
        search_serializers={
            "application/json": "invenio_records_rest.serializers:json_v1_search"
        },
        search_serializers_aliases={
            "json": "application/json",
        },
        list_route="/internal-locations/",
        item_route="/internal-locations/<{0}:pid_value>".format(_ILOCID_CONVERTER),
        default_media_type="application/json",
        max_result_window=RECORDS_REST_MAX_RESULT_WINDOW,
        error_handlers=dict(),
        read_permission_factory_imp=backoffice_read_permission,
        list_permission_factory_imp=backoffice_read_permission,
        create_permission_factory_imp=backoffice_permission,
        update_permission_factory_imp=backoffice_permission,
        delete_permission_factory_imp=backoffice_permission,
    ),
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
    litid=dict(
        # Literature is a search endpoint that allows the user to search in
        # both the documents and series index.
        pid_type=LITERATURE_PID_TYPE,
        pid_minter=LITERATURE_PID_MINTER,
        pid_fetcher=LITERATURE_PID_FETCHER,
        search_class=LiteratureSearch,
        search_factory_imp="shelfmark.literature.search:search_factory_literature",  # noqa
        record_serializers={
            "application/json": (
                "shelfmark.literature.serializers:json_v1_response"
            )
        },
        search_serializers={
            "application/json": "shelfmark.literature.serializers:json_v1_search",
            "text/csv": "shelfmark.literature.serializers:csv_v1_search",
        },
        search_serializers_aliases={
            "csv": "text/csv",
            "json": "application/json",
        },
        item_route="/literature/<pid({}):pid_value>".format(LITERATURE_PID_TYPE),
        list_route="/literature/",
        default_media_type="application/json",
        max_result_window=RECORDS_REST_MAX_RESULT_WINDOW,
        error_handlers=dict(),
        read_permission_factory_imp=deny_all,
        list_permission_factory_imp=allow_all,  # auth via search filter
        create_permission_factory_imp=deny_all,
        update_permission_factory_imp=deny_all,
        delete_permission_factory_imp=deny_all,
    ),
)

# RECORDS REST sort options
# =========================
RECORDS_REST_SORT_OPTIONS = dict(
    eitems=dict(  # ItemSearch.Meta.index
        created=dict(fields=["_created"], title="Recently added", order=1),
        bestmatch=dict(
            fields=["-_score"],
            title="Best match",
            order=2,
        ),
        title=dict(
            fields=["document.title.keyword"],
            title="Title",
            order=3,
        ),
    ),
    items=dict(  # ItemSearch.Meta.index
        created=dict(fields=["_created"], title="Recently added", order=1),
        bestmatch=dict(
            fields=["-_score"],
            title="Best match",
            order=2,
        ),
        title=dict(
            fields=["document.title.keyword"],
            title="Title",
            order=3,
        ),
    ),
    series=dict(  # SeriesSearch.Meta.index
        created=dict(fields=["_created"], title="Recently added", order=1),
        bestmatch=dict(
            fields=["-_score"],
            title="Best match",
            order=2,
        ),
        title=dict(
            fields=["title.keyword"],
            title="Title",
            order=3,
        ),
    ),
)

# RECORDS REST facets
# =========================
#: Number of records to fetch by default
RECORDS_REST_DEFAULT_RESULTS_SIZE = 15

#: Number of tags to display in the DocumentsSearch facet
FACET_TAG_LIMIT = 5

RECORDS_REST_FACETS = dict(
    items=dict(  # ItemSearch.Meta.index
        aggs=dict(
            status=dict(terms=dict(field="status")),
            medium=dict(terms=dict(field="medium")),
            circulation=dict(
                terms=dict(field="circulation.state", missing="NOT_ON_LOAN")
            ),
            restrictions=dict(terms=dict(field="circulation_restriction")),
            location=dict(terms=dict(field="internal_location.location.name")),
            internal_location=dict(terms=dict(field="internal_location.name")),
            document_type=dict(terms=dict(field="document.document_type")),
        ),
        filters=dict(),
        post_filters=dict(
            circulation=default_value_when_missing_filter(
                "circulation.state", "NOT_ON_LOAN"
            ),
            status=terms_filter("status"),
            medium=terms_filter("medium"),
            restrictions=terms_filter("circulation_restriction"),
            location=terms_filter("internal_location.location.name"),
            internal_location=terms_filter("internal_location.name"),
            document_type=terms_filter("document.document_type"),
        ),
    ),
    eitems=dict(
        aggs=dict(
            access=dict(terms=dict(field="open_access")),
            eitem_type=dict(terms=dict(field="eitem_type")),
            has_files=dict(
                filters=dict(
                    filters=dict(
                        has_files=dict(exists=dict(field="files.file_id")),
                        no_files=dict(
                            bool=dict(must_not=dict(exists=dict(field="files.file_id")))
                        ),
                    )
                )
            ),
        ),
        post_filters=dict(
            eitem_type=terms_filter("eitem_type"),
            access=terms_filter("open_access"),
            has_files=exists_value_filter("files.file_id", filter_value="has_files"),
        ),
    ),
    series=dict(  # SeriesSearch.Meta.index
        aggs=dict(
            moi=dict(terms=dict(field="mode_of_issuance")),
            language=dict(terms=dict(field="languages")),
            relation=dict(terms=dict(field="relation_types")),
            sertype=dict(terms=dict(field="series_type")),
        ),
        post_filters=dict(
            moi=terms_filter("mode_of_issuance"),
            language=terms_filter("languages"),
            relation=terms_filter("relation_types"),
            sertype=terms_filter("series_type"),
        ),
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
