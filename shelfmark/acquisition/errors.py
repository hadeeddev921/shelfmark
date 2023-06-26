# SPDX-FileCopyrightText: 2021 CERN.
# SPDX-License-Identifier: MIT

"""Acquisition exceptions."""

from shelfmark.errors import IlsException


class AcquisitionError(IlsException):
    """Raised when there is an error with Acquisition."""

    def __init__(self, description):
        """Initialize exception."""
        super().__init__(description=description)
