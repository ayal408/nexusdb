"""Testcontainers-backed fixtures for real-service integration tests.

Every test under ``tests/integration`` spins up an actual Docker container
(Postgres, MongoDB, Qdrant) instead of mocking the wire protocol, so these
tests validate real driver/exception-mapper behavior. They are auto-marked
``integration`` and auto-skipped when Docker isn't reachable, so a plain
``pytest -m unit`` (e.g. in a Docker-less CI job) is unaffected.
"""

from __future__ import annotations

import pytest


def _docker_available() -> bool:
    try:
        import docker

        docker.from_env().ping()
        return True
    except Exception:
        return False


_DOCKER_AVAILABLE = _docker_available()


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    skip_no_docker = pytest.mark.skip(reason="Docker is not available in this environment")
    for item in items:
        if "tests/integration" in str(item.fspath).replace("\\", "/"):
            item.add_marker(pytest.mark.integration)
            if not _DOCKER_AVAILABLE:
                item.add_marker(skip_no_docker)


@pytest.fixture(scope="session")
def postgres_container():
    from testcontainers.community.postgres import PostgresContainer

    with PostgresContainer("postgres:16-alpine") as container:
        yield container


@pytest.fixture(scope="session")
def postgres_dsn(postgres_container) -> str:
    """Async-driver DSN (``postgresql+asyncpg://...``) for the running container."""

    sync_url = postgres_container.get_connection_url()
    return sync_url.replace("postgresql+psycopg2", "postgresql+asyncpg")


@pytest.fixture(scope="session")
def mongodb_container():
    from testcontainers.community.mongodb import MongoDbContainer

    with MongoDbContainer("mongo:7.0") as container:
        yield container


@pytest.fixture(scope="session")
def mongodb_uri(mongodb_container) -> str:
    # get_connection_url() doesn't include a database segment; our adapter
    # requires one (it calls client.get_default_database()). Appending a
    # path also shifts the driver's default authSource to that database, but
    # the container's root user only exists in "admin", so pin it explicitly.
    return f"{mongodb_container.get_connection_url()}/{mongodb_container.dbname}?authSource=admin"


@pytest.fixture(scope="session")
def qdrant_container():
    from testcontainers.community.qdrant import QdrantContainer

    with QdrantContainer() as container:
        yield container


@pytest.fixture(scope="session")
def qdrant_url(qdrant_container) -> str:
    return f"http://{qdrant_container.rest_host_address}"
