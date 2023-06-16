# Shelfmark

Shelfmark is the backend of an integrated library system (ILS): a REST API, built on the
Invenio framework, that manages a library's catalogue, loans, acquisitions and
interlibrary loans.

## What This Project Does

Running a library means keeping track of what the library owns and where each copy is.
Shelfmark stores this as searchable JSON records and exposes it through a REST API,
which a separate single-page web app uses for both the public catalogue and the
librarian back office.

Main features so far:

- **Catalogue**: documents (books, articles, proceedings and so on), series, physical
  items, electronic items (e-items), and relations between records (editions,
  languages, multipart monographs, serials).
- **Locations**: libraries with opening hours, and internal locations (shelves and
  rooms).
- **Search**: full-text search with facets and CSV export, including a combined
  literature search over documents and series.
- **Permissions**: roles for admins, librarians, read-only librarians and patrons.
- **Vocabularies**: languages, countries, licenses and other controlled lists, loaded
  from the command line.

## How It Works

Shelfmark is a set of Invenio modules. Every library concept (document, item, loan,
order and so on) follows the same pattern:

1. A **JSON Schema** (`schemas/`) defines what a valid record looks like.
2. A **loader** (`loaders/`) validates the incoming JSON from an API request.
3. The **API class** (`api.py`) creates or updates the record in **PostgreSQL** and mints
   a persistent identifier (PID) for it.
4. An **indexer** sends the record to **OpenSearch** using the module's mapping
   (`mappings/`). JSON resolvers expand references (for example, an item's document),
   so the indexed record is complete.
5. **Search classes** (`search.py`) and **permissions** filter what each user can see.
   **Serializers** (`serializers/`) return the result as JSON or CSV.

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Language | Python ≥ 3.9 (Docker image: 3.14) | Application code |
| Web framework | Flask via Invenio (`invenio-app` 3.x, `invenio-base` ≥ 2.3.2) | App factory, CLI and request handling |
| REST API | `invenio-records-rest` 4.x, `invenio-rest` 3.x | CRUD and search endpoints for every record type |
| Records | `invenio-records` 4.x, `invenio-pidstore` 3.x, `jsonschema` ≥ 4.24 | JSON records, persistent identifiers and validation |
| Database | PostgreSQL 14, `invenio-db` 2.x | Record storage |
| Search | OpenSearch (Docker: 3.2.0), `invenio-search[opensearch2]` ≥ 3.1.0, `invenio-indexer` 4.x | Indexing and full-text search |
| Testing | `pytest-invenio` ≥ 3.4.2, `pytest-mock`, `docker-services-cli` ≥ 0.6.0 | Test fixtures and temporary services |
| Packaging | Hatchling | Builds the package from `pyproject.toml` |

## How to Run This Project

The application is still being assembled. These steps prepare a development
environment.

### 1. Prerequisites

- Python 3.9 or newer
- Docker and Docker Compose

### 2. Clone

```bash
git clone https://github.com/hadeeddev921/shelfmark.git
cd shelfmark
```

### 3. Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[opensearch2]"
```

### 4. Environment variables

Every setting in `shelfmark/config.py` can be overridden with an environment variable
prefixed with `INVENIO_`. Copy the example file and load it into your shell:

```bash
cp .env.example .env
set -a; source .env; set +a
```

See `.env.example` for the database, Redis, RabbitMQ and OpenSearch settings.

### 5. Start the services

```bash
docker compose up -d
```

This starts PostgreSQL, Redis, RabbitMQ, OpenSearch and OpenSearch Dashboards.
