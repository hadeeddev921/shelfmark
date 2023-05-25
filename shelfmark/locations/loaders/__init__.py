# SPDX-FileCopyrightText: 2020 CERN.
# SPDX-License-Identifier: MIT

"""ILS Locations loaders."""

from shelfmark.locations.loaders.jsonschemas.location import LocationSchemaV1
from shelfmark.records.loaders import ils_marshmallow_loader

location_loader = ils_marshmallow_loader(LocationSchemaV1)
