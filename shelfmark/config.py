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
