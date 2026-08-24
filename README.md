# nexusdb

An enterprise-grade, multi-database Python library that provides a unified
interface and repository pattern over relational (PostgreSQL/MySQL/SQLite),
document (MongoDB), and vector (Qdrant) databases.

> **Status:** foundational scaffold — core interfaces, exception mapping,
> resilience primitives, and the test harness are in place. Concrete adapters
> (Postgres/MySQL/SQLite/MongoDB/Qdrant), the SQLAlchemy Unit of Work, Redis
> cache, and the outbox relay are the next milestones.

## Why

Most projects that touch more than one kind of database end up with
per-backend, ad-hoc data access code, inconsistent error handling, and no
shared story for retries, caching, multi-tenancy, or observability. nexusdb
gives every backend the same repository/Unit-of-Work surface, the same
exception hierarchy, and the same resilience and observability behavior, so
application code depends on `nexusdb`'s abstractions instead of a specific
driver.

## Architecture at a glance

```
src/nexusdb/
├── core/            settings, enums, the exception hierarchy, the driver
│                     exception mapper, structlog config, correlation/tenant
│                     context (contextvars)
├── interfaces/       ABCs: AbstractDatabaseAdapter, AbstractRepository,
│                     AbstractUnitOfWork, AbstractCache, domain events/outbox
├── adapters/         concrete backends, one package per DB family
│   ├── relational/    PostgreSQL / MySQL / SQLite via async SQLAlchemy,
│   │                  with master/replica read-write splitting
│   ├── document/      MongoDB via Motor
│   └── vector/        Qdrant
├── repositories/     backend-specific AbstractRepository implementations
├── uow/               Unit of Work implementations
├── cache/             Redis-backed cache-aside implementation
├── resilience/        circuit breaker + exponential-backoff retry
├── events/             in-process dispatcher + transactional outbox
├── observability/     metrics, tracing, audit trail
├── multitenancy/      tenant isolation helpers
├── factory/            DatabaseFactory: builds/owns every configured adapter
├── models/             shared Pydantic base models (Entity, AuditRecord)
└── cli/                `nexusdb` console script (init, health, ...)
```

Every domain entity is a Pydantic v2 model; every mutating repository method
supports an idempotency key; every raised error is a `NexusDBError` subclass
(driver exceptions are translated centrally in
`core/exception_mapper.py`, never leaked to callers).

## Installation

```bash
pip install -e ".[dev]"          # core + dev/test tooling
pip install -e ".[postgres]"     # + asyncpg
pip install -e ".[all]"          # everything
```

## Testing

```bash
pytest -m unit                   # fast, no external services required
pytest -m integration            # spins up real Postgres/MongoDB/Qdrant
                                  # containers via Testcontainers (needs Docker)
pytest                           # everything
```

Integration tests are automatically skipped when Docker isn't reachable, so
`pytest -m unit` (or plain `pytest` in a Docker-less environment) never fails
because of them.

## License

MIT — see [LICENSE](LICENSE).
