# SPDX-FileCopyrightText: 2020 CERN.
# SPDX-License-Identifier: MIT

"""ILS Items serializers."""

from invenio_records_rest.serializers.response import search_responsify

from shelfmark.records.schemas.json import ILSRecordSchemaJSONV1
from shelfmark.records.serializers import record_responsify_no_etag

from .item import ItemCSVSerializer, ItemJSONSerializer

csv_v1 = ItemCSVSerializer(ILSRecordSchemaJSONV1, csv_excluded_fields=[])
csv_v1_response = record_responsify_no_etag(csv_v1, "text/csv")
csv_v1_search = search_responsify(csv_v1, "text/csv")

json_v1 = ItemJSONSerializer(ILSRecordSchemaJSONV1, replace_refs=True)
json_v1_response = record_responsify_no_etag(json_v1, "application/json")
json_v1_search = search_responsify(json_v1, "application/json")
