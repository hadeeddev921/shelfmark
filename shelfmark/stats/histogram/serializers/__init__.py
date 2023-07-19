# SPDX-FileCopyrightText: 2025-2025 CERN.
# SPDX-License-Identifier: MIT

"""Shelfmark histogram stats serializers."""

from shelfmark.stats.histogram.serializers.response import (
    histogram_stats_responsify,
)
from shelfmark.stats.histogram.serializers.schema import HistogramStatsV1

histogram_stats_response = histogram_stats_responsify(
    HistogramStatsV1, "application/json"
)
