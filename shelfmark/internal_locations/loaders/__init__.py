# SPDX-FileCopyrightText: 2020 CERN.
# SPDX-License-Identifier: MIT

"""ILS internal locations loaders."""

from shelfmark.internal_locations.loaders.jsonschemas.internal_location import (  # noqa
    InternalLocationSchemaV1,
)
from shelfmark.records.loaders import ils_marshmallow_loader

internal_location_loader = ils_marshmallow_loader(InternalLocationSchemaV1)
