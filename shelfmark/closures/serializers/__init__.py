# SPDX-FileCopyrightText: 2025-2025 CERN.
# SPDX-License-Identifier: MIT


from shelfmark.closures.serializers.response import closure_periods_responsify
from shelfmark.closures.serializers.schema import ClosurePeriodsV1


closure_periods_response = closure_periods_responsify(
    ClosurePeriodsV1, "application/json"
)
