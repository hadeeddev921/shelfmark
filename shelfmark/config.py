# SPDX-FileCopyrightText: 2018-2025 CERN.
# SPDX-License-Identifier: MIT

"""Default configuration for shelfmark.

You overwrite and set instance-specific configuration by either:

- Configuration file: ``<virtualenv prefix>/var/instance/invenio.cfg``
- Environment variables: ``APP_<variable name>``
"""


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
