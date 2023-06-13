# SPDX-FileCopyrightText: 2020 CERN.
# SPDX-License-Identifier: MIT

"""ILS items loaders."""

from shelfmark.items.loaders.jsonschemas.items import ItemSchemaV1
from shelfmark.records.loaders import ils_marshmallow_loader

item_loader = ils_marshmallow_loader(ItemSchemaV1)
