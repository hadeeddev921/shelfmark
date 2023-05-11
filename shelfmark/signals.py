# SPDX-FileCopyrightText: 2019 CERN.
# SPDX-License-Identifier: MIT

"""Shelfmark signals."""

from blinker import Namespace

_signals = Namespace()

record_viewed = _signals.signal("record-viewed")
file_downloaded = _signals.signal("file-downloaded")
