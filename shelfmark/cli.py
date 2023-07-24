# SPDX-FileCopyrightText: 2018-2026 CERN.
# SPDX-License-Identifier: MIT

"""CLI for Shelfmark."""
import json
import os
import pathlib
import random
from datetime import date, timedelta
from random import randint

import arrow
import lorem
from flask import current_app
from invenio_circulation.api import Loan
from invenio_circulation.pidstore.pids import CIRCULATION_LOAN_PID_TYPE
from invenio_db import db
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_pidstore.providers.recordid_v2 import RecordIdProviderV2
from lorem.text import TextLorem
from .documents.api import DOCUMENT_PID_TYPE, Document
from .eitems.api import EITEM_PID_TYPE, EItem
from .internal_locations.api import INTERNAL_LOCATION_PID_TYPE, InternalLocation
from .items.api import ITEM_PID_TYPE, Item
from .locations.api import LOCATION_PID_TYPE, Location
from .proxies import current_app_ils
from .series.api import SERIES_PID_TYPE, Series

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


class EItemGenerator(Generator):
    """EItem Generator."""

    def generate(self):
        """Generate."""
        size = self.holder.eitems["total"]
        doc_pids = self.holder.pids("documents", "pid")

        objs = [
            {
                "pid": self.create_pid(),
                "created_by": {
                    "type": "script",
                    "value": "demo",
                },
                "document_pid": random.choice(doc_pids),
                "eitem_type": random.choice(EItem.EITEM_TYPES),
                "description": "{}".format(lorem.text()),
                "internal_notes": "{}".format(lorem.text()),
                "urls": [
                    {
                        "value": "https://home.cern/science/physics/a",
                        "description": "Dark matter",
                    },
                    {
                        "value": "https://home.cern/science/physics/b",
                        "description": "Anti matter",
                    },
                ],
                "open_access": bool(random.getrandbits(1)),
            }
            for pid in range(1, size + 1)
        ]

        for obj in objs:
            if bool(random.getrandbits(1)):
                obj["identifiers"] = random.choice(
                    [
                        [
                            {
                                "scheme": "ISBN",
                                "value": "0-395-36341-1",
                                "material": "EBook",
                            },
                            {
                                "scheme": "DOI",
                                "value": "doi:10.1340/309registries",
                            },
                        ],
                        [],
                    ]
                )

        self.holder.eitems["objs"] = objs

    def persist(self):
        """Persist."""
        recs = []
        for obj in self.holder.eitems["objs"]:
            rec = self._persist(EITEM_PID_TYPE, "pid", EItem.create(obj))
            recs.append(rec)
        db.session.commit()
        return recs


class DocumentGenerator(Generator):
    """Document Generator."""

    SERIAL_ISSUE = "SERIAL_ISSUE"
    AUTHORS = [
        {"full_name": "Close, Frank"},
        {"full_name": "Harrison, Stacey"},
        {"full_name": "Glover, Bruno"},
        {"full_name": "CERN", "type": "ORGANISATION"},
        {
            "full_name": "Doe, Jane",
            "affiliations": [
                {
                    "name": "Imperial Coll., London",
                    "identifiers": [{"scheme": "ROR", "value": "12345"}],
                }
            ],
            "identifiers": [{"scheme": "ORCID", "value": "1234AAA"}],
            "roles": ["EDITOR"],
        },
        {
            "full_name": "Haigh, Jill",
            "roles": ["RESEARCHER"],
            "affiliations": [{"name": "CERN"}],
        },
    ]
    CONFERENCE_INFO = [
        {
            "acronym": "CHEP",
            "country": "AUS",
            "dates": "1 - 20 Nov. 2019",
            "identifiers": [{"scheme": "OTHER", "value": "CHEP2019"}],
            "place": "Adelaide",
            "series": "CHEP",
            "title": "Conference on Computing in High Energy Physics",
            "year": 2019,
        },
        {
            "place": "London",
            "title": "Conference on Physics in High Energy Physics",
        },
    ]
    IMPRINTS = [
        {"date": "2019-08-02", "place": "Geneva", "publisher": "CERN"},
        {"date": "2017-08-02", "place": "Hamburg", "publisher": "Springer"},
    ]
    ISBNS = [
        "0002154129",
        "978-1-891830-85-3",
        "978-1-60309-265-4",
        "978-1-60309-077-3",
        "978-1-60309-069-8",
        "978-1-60309-042-1",
        "978-1-891830-37-2",
        "978-1-60309-029-2",
        "978-1-891830-40-2",
        "978-1-60309-442-9",
        "978-1-891830-56-3",
        "978-1-60309-432-0",
        "978-1-891830-19-8",
        "978-1-60309-422-1",
        "978-1-60309-100-8",
        "978-1-891830-81-5",
        "978-1-60309-271-5",
        "978-1-891830-92-1",
        "978-1-60309-057-5",
        "978-1-60309-085-8",
        "978-1-60309-387-3",
        "978-1-60309-036-0",
        "978-1-60309-053-7",
        "978-1-891830-97-6",
        "978-0-9585783-4-9",
        "978-1-60309-397-2",
        "978-1-60309-386-6",
        "978-1-60309-098-8",
        "978-1-60309-008-7",
        "978-1-60309-441-2",
        "978-1-891830-55-6",
        "978-1-891830-86-0",
        "978-1-891830-91-4",
        "978-1-60309-041-4",
        "978-1-60309-059-9",
        "978-1-891830-65-5",
        "978-1-891830-90-7",
        "978-1-60309-006-3",
        "978-1-60309-007-0",
        "978-1-60309-437-5",
        "978-1-891830-51-8",
        "978-1-60309-070-4",
        "978-1-63140-984-4",
        "978-1-60309-393-4",
        "978-1-60309-152-7",
        "978-1-891830-33-4",
        "978-1-60309-300-2",
        "978-1-60309-383-5",
        "978-1-60309-400-9",
        "978-1-891830-36-5",
        "978-1-60309-075-9",
        "978-1-891830-68-6",
        "978-1-60309-049-0",
        "978-1-60309-409-2",
        "978-1-60309-068-1",
        "978-1-891830-29-7",
        "978-1-60309-367-5",
        "978-1-60309-413-9",
        "978-1-60309-089-6",
        "978-1-60309-445-0",
        "978-1-891830-14-3",
        "978-1-891830-50-1",
        "978-1-60309-020-9",
        "978-1-60309-031-5",
        "978-1-60309-055-1",
        "978-1-891830-96-9",
        "978-1-60309-043-8",
        "978-1-891830-87-7",
        "978-1-60309-033-9",
        "978-1-60309-005-6",
        "978-1-60309-450-4",
        "978-1-891830-31-0",
        "978-1-891830-70-9",
        "978-1-891830-98-3",
        "978-1-60309-392-7",
        "978-1-60309-074-2",
        "978-1-891830-41-9",
        "978-1-60309-088-9",
        "978-1-60309-440-5",
    ]

    LICENSE = {
        "license": {
            "id": "license-0bsd",
        },
        "material": "paper",
    }

    COPYRIGHTS = {
        "holder": "INSTITUTION",
        "material": "paper",
        "statement": "Copyright statement",
        "url": "https://test.com",
        "year": 1990,
    }

    def generate_document(self, index, **kwargs):
        """Generate document data."""
        publication_year = kwargs.get("publication_year", str(randint(1700, 2020)))
        imprint = random.choice(self.IMPRINTS)
        isbn = random.choice(self.ISBNS)
        n_authors = randint(1, len(self.AUTHORS))
        obj = {
            "pid": self.create_pid(),
            "title": lorem.sentence(),
            "cover_metadata": {"ISBN": isbn, "urls": {}},
            "copyrights": [self.COPYRIGHTS],
            "authors": random.sample(self.AUTHORS, n_authors),
            "abstract": "{}".format(lorem.text()),
            "document_type": random.choice(Document.DOCUMENT_TYPES),
            "created_by": {"type": "script", "value": "demo"},
            "languages": [
                lang["key"]
                for lang in random.sample(self.holder.languages, randint(1, 3))
            ],
            "table_of_content": ["{}".format(lorem.sentence())],
            "note": "{}".format(lorem.text()),
            "tags": [
                tag["key"]
                for tag in random.sample(
                    self.holder.tags, randint(1, len(self.holder.tags) - 1)
                )
            ],
            "edition": str(index),
            "keywords": [{"source": lorem.sentence(), "value": lorem.sentence()}],
            "conference_info": self.CONFERENCE_INFO,
            "number_of_pages": str(random.randint(0, 300)),
            "identifiers": [{"scheme": "ISBN", "value": isbn}],
            "alternative_identifiers": [{"scheme": "ARXIV", "value": "1234.1234"}],
            "imprint": {
                **imprint,
                "date": "{}-08-02".format(publication_year),
            },
            "licenses": [self.LICENSE],
            "publication_year": publication_year,
            "subjects": [{"value": "515.353", "scheme": "Dewey"}],
            "urls": [
                {
                    "description": "{}".format(lorem.sentence()),
                    "value": "http://random.url",
                }
            ],
            "restricted": False,
        }
        obj.update(**kwargs)
        return obj

    def generate(self):
        """Generate."""
        size = self.holder.documents["total"]

        objs = [self.generate_document(index) for index in range(1, size + 1)]

        # Generate periodical issues
        volume = 1
        issue = 1
        publication_year = randint(1700, 2000)
        for index in range(1, 11):
            objs.append(
                self.generate_document(
                    index,
                    document_type=self.SERIAL_ISSUE,
                    title="Volume {} Issue {}".format(volume, issue),
                    publication_year=str(publication_year),
                )
            )
            if issue == 3:
                issue = 1
                volume += 1
                publication_year += 1
            else:
                issue += 1

        demo_data_dir = os.path.join(CURRENT_DIR, "demo_data")
        with open(os.path.join(demo_data_dir, "documents.json")) as f:
            demo_data = json.loads(f.read())

        for doc in demo_data:
            doc["pid"] = self.create_pid()

        objs.extend(demo_data)
        self.holder.documents["objs"] = objs

    def persist(self):
        """Persist."""
        recs = []
        for obj in self.holder.documents["objs"]:
            rec = self._persist(DOCUMENT_PID_TYPE, "pid", Document.create(obj))
            recs.append(rec)
        db.session.commit()
        return recs


class LoanGenerator(Generator):
    """Loan Generator."""

    LOAN_STATES = ["PENDING", "ITEM_ON_LOAN", "ITEM_RETURNED", "CANCELLED"]

    def _get_item_can_circulate(self, items):
        """Return an item that can circulate."""
        item = items[randint(1, len(items) - 1)]
        if item["status"] != "CAN_CIRCULATE":
            return self._get_item_can_circulate(items)
        return item

    def _get_valid_status(self, item, items_on_loan):
        """Return valid loan status for the item to avoid inconsistencies."""
        # cannot have 2 loans in the same item
        if item["pid"] in items_on_loan:
            status = self.LOAN_STATES[0]
        else:
            status = self.LOAN_STATES[randint(0, 3)]
        return status

    def _fill_loan_with_valid_request(self, loan):
        """Add fields to the loan with dates valid for a request."""
        transaction_date = arrow.utcnow() - timedelta(days=randint(1, 10))
        request_start_date = transaction_date + timedelta(days=15)
        request_expire_date = transaction_date + timedelta(days=180)
        loan["transaction_date"] = transaction_date.isoformat()
        loan["request_start_date"] = request_start_date.date().isoformat()
        loan["request_expire_date"] = request_expire_date.date().isoformat()

    def _fill_loan_with_valid_loan(self, loan):
        """Add fields to the loan with dates valid for a on-going loan."""
        transaction_date = arrow.utcnow() - timedelta(days=randint(20, 30))
        start_date = transaction_date - timedelta(days=randint(1, 5))
        end_date = start_date + timedelta(days=30)
        loan["transaction_date"] = transaction_date.isoformat()
        loan["start_date"] = start_date.date().isoformat()
        loan["end_date"] = end_date.date().isoformat()
        loan["extension_count"] = randint(0, 3)

    def _fill_loan_with_loan_returned(self, loan):
        """Add fields to the loan with dates valid for a returned loan."""
        transaction_date = arrow.utcnow() - timedelta(days=randint(50, 70))
        start_date = transaction_date - timedelta(days=randint(40, 50))
        end_date = start_date + timedelta(days=30)
        loan["transaction_date"] = transaction_date.isoformat()
        loan["start_date"] = start_date.date().isoformat()
        loan["end_date"] = end_date.date().isoformat()

    def _fill_loan_with_loan_cancelled(self, loan):
        """Add fields to the loan with dates valid for a cancelled loan."""
        transaction_date = arrow.utcnow() - timedelta(days=randint(50, 100))
        request_expire_date = transaction_date + timedelta(days=180)
        start_date = transaction_date - timedelta(days=randint(40, 50))
        end_date = start_date + timedelta(days=30)
        loan["transaction_date"] = transaction_date.isoformat()
        loan["request_expire_date"] = request_expire_date.date().isoformat()
        loan["start_date"] = start_date.date().isoformat()
        loan["end_date"] = end_date.date().isoformat()
        loan["cancel_reason"] = "{}".format(lorem.sentence())

    def _fill_loan(self, loan):
        """Fill loan with valid dates."""
        if loan["state"] == "PENDING":
            self._fill_loan_with_valid_request(loan)
        elif loan["state"] == "ITEM_ON_LOAN":
            self._fill_loan_with_valid_loan(loan)
        elif loan["state"] == "ITEM_RETURNED":
            self._fill_loan_with_loan_returned(loan)
        elif loan["state"] == "CANCELLED":
            self._fill_loan_with_loan_cancelled(loan)
        return loan

    def generate(self):
        """Generate."""
        size = self.holder.loans["total"]
        loc_pid, _ = current_app_ils.get_default_location_pid
        items = self.holder.items["objs"]
        patrons_pids = self.holder.patrons_pids
        librarian_pid = self.holder.librarian_pid
        doc_pids = self.holder.pids("documents", "pid")
        all_delivery_methods = list(
            current_app.config["ILS_CIRCULATION_DELIVERY_METHODS"].keys()
        )
        delivery = all_delivery_methods[randint(0, 1)]

        items_on_loan = []
        for pid in range(1, size + 1):
            item = self._get_item_can_circulate(items)
            item_state = self._get_valid_status(item, items_on_loan)
            patron_id = random.choice(patrons_pids)

            loan = {
                "pid": self.create_pid(),
                "document_pid": random.choice(doc_pids),
                "patron_pid": "{}".format(patron_id),
                "pickup_location_pid": "{}".format(loc_pid),
                "state": "{}".format(item_state),
                "transaction_location_pid": "{}".format(loc_pid),
                "transaction_user_pid": "{}".format(librarian_pid),
                "delivery": {"method": delivery},
            }
            loan = self._fill_loan(loan)

            if item_state != "PENDING":
                loan["item_pid"] = {
                    "type": ITEM_PID_TYPE,
                    "value": item["pid"],
                }
                items_on_loan.append(item["pid"])

            self.holder.loans["objs"].append(loan)

    def persist(self):
        """Persist."""
        recs = []
        for obj in self.holder.loans["objs"]:
            rec = self._persist(CIRCULATION_LOAN_PID_TYPE, "pid", Loan.create(obj))
            recs.append(rec)
        db.session.commit()
        return recs


class SeriesGenerator(Generator):
    """Series Generator."""

    MODE_OF_ISSUANCE = Series.MODE_OF_ISSUANCE

    def random_issn(self):
        """Generate a random ISSN."""
        random_4digit = [randint(1000, 9999), randint(1000, 9999)]
        return "-".join(str(r) for r in random_4digit)

    def random_multipart(self, obj, index):
        """Randomize multipart data."""
        obj["edition"] = str(index)
        for _ in range(randint(1, 2)):
            obj["identifiers"].append(
                dict(scheme="ISBN", value=random.choice(DocumentGenerator.ISBNS))
            )

    def random_serial(self, obj):
        """Randomize serial data."""
        for _ in range(randint(1, 3)):
            obj["identifiers"].append(
                dict(
                    material=random.choice(["ONLINE", "PRINT"]),
                    scheme="ISSN",
                    value=self.random_issn(),
                )
            )
        obj["abbreviated_title"] = obj["title"].split()[0]
        obj["alternative_titles"] = [
            dict(value=obj["title"], type="SUBTITLE"),
            dict(value=obj["title"].split()[0], type="ABBREVIATION"),
            dict(
                value=obj["title"],
                type="TRANSLATED_TITLE",
                language="FRA",
            ),
        ]
        obj["internal_notes"] = [
            dict(field="title", user="Test", value="Internal test note.")
        ]
        obj["notes"] = lorem.text()
        obj["publisher"] = lorem.sentence().split()[0]
        obj["access_urls"] = [
            dict(
                open_access=True,
                description=lorem.sentence(),
                value="https://home.cern/",
            )
            for _ in range(1, 3)
        ]
        obj["urls"] = [
            dict(description=lorem.sentence(), value="https://home.cern/")
            for _ in range(1, 3)
        ]

    def generate_minimal(self, objs):
        """Generate a series with only the required fields."""
        objs.append(
            {
                "pid": self.create_pid(),
                "mode_of_issuance": "SERIAL",
                "title": "Minimal Series",
            }
        )

    def generate(self):
        """Generate."""
        size = self.holder.series["total"]
        objs = []
        self.generate_minimal(objs)
        for index in range(1, size + 1):
            moi = random.choice(self.MODE_OF_ISSUANCE)
            authors = random.sample(
                DocumentGenerator.AUTHORS, len(DocumentGenerator.AUTHORS)
            )
            obj = {
                "pid": self.create_pid(),
                "cover_metadata": {
                    "ISBN": random.choice(DocumentGenerator.ISBNS),
                    "urls": {},
                },
                "mode_of_issuance": moi,
                "title": lorem.sentence(),
                "authors": [author["full_name"] for author in authors],
                "abstract": lorem.text(),
                "languages": [
                    lang["key"]
                    for lang in random.sample(self.holder.languages, randint(1, 3))
                ],
                "identifiers": [],
                "created_by": {"type": "script", "value": "demo"},
                "tags": [
                    tag["key"]
                    for tag in random.sample(
                        self.holder.tags, randint(1, len(self.holder.tags) - 1)
                    )
                ],
                "keywords": [{"source": lorem.sentence(), "value": lorem.sentence()}],
                "series_type": random.choice(Series.SERIES_TYPES),
            }
            if moi == "SERIAL":
                self.random_serial(obj)
            elif moi == "MULTIPART_MONOGRAPH":
                self.random_multipart(obj, index)
            objs.append(obj)

        self.holder.series["objs"] = objs

    def persist(self):
        """Persist."""
        recs = []
        for obj in self.holder.series["objs"]:
            rec = self._persist(SERIES_PID_TYPE, "pid", Series.create(obj))
            recs.append(rec)
        db.session.commit()
        return recs
