# SPDX-FileCopyrightText: 2020-2021 CERN.
# SPDX-License-Identifier: MIT

"""Shelfmark Document Request Decline loader JSON schema."""

from invenio_records_rest.schemas import RecordMetadataSchemaJSONV1
from marshmallow import EXCLUDE, fields, validate

from shelfmark.document_requests.api import DocumentRequest


class DocumentRequestDeclineSchemaV1(RecordMetadataSchemaJSONV1):
    """Document Request Decline schema."""

    class Meta:
        """Meta attributes for the schema."""

        unknown = EXCLUDE

    document_pid = fields.Str()
    decline_reason = fields.Str(
        required=True, validate=validate.OneOf(DocumentRequest.DECLINE_TYPES)
    )
