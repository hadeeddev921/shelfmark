# SPDX-FileCopyrightText: 2020 CERN.
# SPDX-License-Identifier: MIT

"""Shelfmark ILL errors."""

from shelfmark.errors import IlsException


class ILLError(IlsException):
    """Raised when there is an error with an InterLibrary Loan."""

    def __init__(self, description):
        """Initialize exception."""
        super().__init__(description=description)
