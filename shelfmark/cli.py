# SPDX-FileCopyrightText: 2018-2026 CERN.
# SPDX-License-Identifier: MIT

"""CLI for Shelfmark."""
import pathlib
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_pidstore.providers.recordid_v2 import RecordIdProviderV2

CURRENT_DIR = pathlib.Path(__file__).parent.absolute()


def minter(pid_type, pid_field, record):
    """Mint the given PID for the given record."""
    pid = PersistentIdentifier.get(pid_type="recid", pid_value=record[pid_field])
    pid.status = PIDStatus.REGISTERED
    pid.object_type = "rec"
    pid.object_uuid = record.id
    pid.pid_type = pid_type


class Holder(object):
    """Hold generated data."""

    def __init__(
        self,
        patrons_pids,
        languages,
        librarian_pid,
        tags,
        total_intloc,
        total_items,
        total_eitems,
        total_documents,
        total_loans,
        total_series,
        total_document_requests,
        total_vendors,
        total_orders,
        total_borrowing_requests,
        total_libraries,
    ):
        """Constructor."""
        self.patrons_pids = patrons_pids
        self.languages = languages
        self.librarian_pid = librarian_pid
        self.tags = tags
        self.internal_locations = {"objs": [], "total": total_intloc}
        self.items = {"objs": [], "total": total_items}
        self.eitems = {"objs": [], "total": total_eitems}
        self.documents = {"objs": [], "total": total_documents}
        self.loans = {"objs": [], "total": total_loans}
        self.series = {"objs": [], "total": total_series}
        self.related_records = {"objs": [], "total": 0}
        self.document_requests = {"objs": [], "total": total_document_requests}
        self.vendors = {"objs": [], "total": total_vendors}
        self.orders = {"objs": [], "total": total_orders}
        self.borrowing_requests = {
            "objs": [],
            "total": total_borrowing_requests,
        }
        self.pending_borrowing_requests = {"objs": []}
        self.libraries = {"objs": [], "total": total_libraries}

    def pids(self, collection, pid_field):
        """Get a list of PIDs for a collection."""
        return [obj[pid_field] for obj in getattr(self, collection)["objs"]]


class Generator(object):
    """Generator."""

    def __init__(self, holder, minter):
        """Constructor."""
        self.holder = holder
        self.minter = minter

    def create_pid(self):
        """Create a new persistent identifier."""
        return RecordIdProviderV2.create().pid.pid_value

    def _persist(self, pid_type, pid_field, record):
        """Mint PID and store in the db."""
        minter(pid_type, pid_field, record)
        return record
