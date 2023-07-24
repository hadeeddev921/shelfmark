# SPDX-FileCopyrightText: 2018-2026 CERN.
# SPDX-License-Identifier: MIT

"""CLI for Shelfmark."""
import json
import os
import pathlib
import random
from datetime import date, timedelta
from random import randint
import lorem
from invenio_db import db
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_pidstore.providers.recordid_v2 import RecordIdProviderV2
from lorem.text import TextLorem
from .internal_locations.api import INTERNAL_LOCATION_PID_TYPE, InternalLocation
from .items.api import ITEM_PID_TYPE, Item
from .locations.api import LOCATION_PID_TYPE, Location
from .proxies import current_app_ils

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


class LocationGenerator(Generator):
    """Location Generator."""

    def generate(self):
        """Generate."""
        weekdays = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]
        closed = ["saturday", "sunday"]
        times = [
            {"start_time": "08:00", "end_time": "12:00"},
            {"start_time": "13:00", "end_time": "18:00"},
        ]
        opening_weekdays = []
        for weekday in weekdays:
            is_open = weekday not in closed
            opening_weekdays.append(
                {
                    "weekday": weekday,
                    "is_open": weekday not in closed,
                    **({"times": times} if is_open else {}),
                }
            )
        last_date = date.today()
        opening_exceptions = []
        for i in range(randint(0, 3)):
            start_date = last_date + timedelta(days=randint(1, 15))
            end_date = start_date + timedelta(days=randint(1, 4))
            last_date = end_date
            opening_exceptions.append(
                {
                    "title": lorem.sentence(),
                    "is_open": random.random() >= 0.7,
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                }
            )
        self.holder.location = {
            "pid": self.create_pid(),
            "name": "Central Library",
            "address": "Rue de Meyrin",
            "email": "library@cern.ch",
            "opening_weekdays": opening_weekdays,
            "opening_exceptions": opening_exceptions,
        }

    def persist(self):
        """Persist."""
        record = Location.create(self.holder.location)
        rec = self._persist(LOCATION_PID_TYPE, "pid", record)
        db.session.commit()
        return rec


class InternalLocationGenerator(Generator):
    """InternalLocation Generator."""

    def generate(self):
        """Generate."""
        size = self.holder.internal_locations["total"]
        location_pid_value, _ = current_app_ils.get_default_location_pid
        objs = [
            {
                "pid": self.create_pid(),
                "legacy_id": randint(100000, 999999),
                "name": "Building {}".format(randint(1, 10)),
                "notes": lorem.sentence(),
                "physical_location": lorem.sentence(),
                "location_pid": location_pid_value,
                "restricted": False,
            }
            for pid in range(1, size + 1)
        ]

        self.holder.internal_locations["objs"] = objs

    def persist(self):
        """Persist."""
        recs = []
        for obj in self.holder.internal_locations["objs"]:
            rec = self._persist(
                INTERNAL_LOCATION_PID_TYPE, "pid", InternalLocation.create(obj)
            )
            recs.append(rec)
        db.session.commit()
        return recs


class ItemGenerator(Generator):
    """Item Generator."""

    MEDIUMS = [
        "NOT_SPECIFIED",
        "PAPER",
        "CDROM",
        "DVD",
        "VHS",
    ]

    def generate(self):
        """Generate."""
        size = self.holder.items["total"]
        iloc_pids = self.holder.pids("internal_locations", "pid")
        doc_pids = self.holder.pids("documents", "pid")
        shelf_lorem = TextLorem(wsep="-", srange=(2, 3), words="Ax Bs Cw 8080".split())
        objs = [
            {
                "pid": self.create_pid(),
                "created_by": {
                    "type": "script",
                    "value": "demo",
                },
                "document_pid": random.choice(doc_pids),
                "internal_location_pid": random.choice(iloc_pids),
                "isbns": [{"value": "978-1-891830-85-3"}],
                "legacy_id": "{}".format(randint(100000, 999999)),
                "legacy_library_id": "{}".format(randint(5, 50)),
                "barcode": "{}".format(randint(10000000, 99999999)),
                "shelf": "{}".format(shelf_lorem.sentence()),
                "description": "{}".format(lorem.text()),
                "internal_notes": "{}".format(lorem.text()),
                "medium": random.choice(self.MEDIUMS),
                "status": random.choice(
                    random.choices(
                        population=Item.STATUSES,
                        weights=[0.7, 0.1, 0.1, 0.1, 0.05],
                        k=10,
                    )
                ),
                "circulation_restriction": random.choice(Item.CIRCULATION_RESTRICTIONS),
            }
            for pid in range(1, size + 1)
        ]

        demo_data_dir = os.path.join(CURRENT_DIR, "demo_data")
        with open(os.path.join(demo_data_dir, "items.json")) as f:
            demo_data = json.loads(f.read())

        for item in demo_data:
            item["pid"] = self.create_pid()
            item["document_pid"] = random.choice(doc_pids)
            item["internal_location_pid"] = random.choice(iloc_pids)

        objs.extend(demo_data)
        self.holder.items["objs"] = objs

    def persist(self):
        """Persist."""
        recs = []
        for obj in self.holder.items["objs"]:
            rec = self._persist(ITEM_PID_TYPE, "pid", Item.create(obj))
            recs.append(rec)
        db.session.commit()
        return recs
