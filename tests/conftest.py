"""Shared fixtures for the whole test suite (unit + integration)."""

from __future__ import annotations

import uuid
from collections.abc import Mapping, Sequence
from typing import Any

import pytest

from nexusdb.core.logging import configure_logging
from nexusdb.interfaces.repository import AbstractRepository, BulkResult, Page, SortSpec
from nexusdb.models.base import Entity


def pytest_configure(config: pytest.Config) -> None:
    configure_logging(json_output=False)


class Widget(Entity):
    """Minimal domain entity used across unit tests."""

    name: str
    quantity: int = 0


class InMemoryWidgetRepository(AbstractRepository[Widget, uuid.UUID]):
    """A trivial in-memory implementation of the repository contract.

    Exists purely so unit tests can exercise the ABC's default behavior
    (``get_by_id_or_raise``, ``exists``) and so it can double as a reference
    implementation when writing new backend-specific repositories.
    """

    model = Widget

    def __init__(self) -> None:
        self._store: dict[uuid.UUID, Widget] = {}

    async def get_by_id(self, id_: uuid.UUID) -> Widget | None:
        return self._store.get(id_)

    async def create(self, entity: Widget, *, idempotency_key: str | None = None) -> Widget:
        self._store[entity.id] = entity
        return entity

    async def update(self, id_: uuid.UUID, changes: Mapping[str, Any]) -> Widget:
        from nexusdb.core.exceptions import RecordNotFoundError

        current = self._store.get(id_)
        if current is None:
            raise RecordNotFoundError("Widget", id_)
        updated = current.model_copy(update=dict(changes))
        self._store[id_] = updated
        return updated

    async def delete(self, id_: uuid.UUID) -> bool:
        return self._store.pop(id_, None) is not None

    async def find(
        self,
        criteria: Mapping[str, Any] | None = None,
        *,
        limit: int = 50,
        offset: int = 0,
        sort: Sequence[SortSpec] | None = None,
    ) -> Page[Widget]:
        items = list(self._store.values())
        if criteria:
            items = [
                w for w in items if all(getattr(w, k, None) == v for k, v in criteria.items())
            ]
        total = len(items)
        return Page(items=items[offset : offset + limit], total=total, limit=limit, offset=offset)

    async def count(self, criteria: Mapping[str, Any] | None = None) -> int:
        page = await self.find(criteria, limit=len(self._store) or 1)
        return page.total or 0

    async def bulk_create(
        self, entities: Sequence[Widget], *, idempotency_key: str | None = None
    ) -> BulkResult[Widget]:
        succeeded = []
        for entity in entities:
            self._store[entity.id] = entity
            succeeded.append(entity)
        return BulkResult(succeeded=succeeded)

    async def bulk_update(self, updates: Mapping[uuid.UUID, Mapping[str, Any]]) -> BulkResult[Widget]:
        succeeded, failed = [], {}
        for idx, (id_, changes) in enumerate(updates.items()):
            try:
                succeeded.append(await self.update(id_, changes))
            except Exception as exc:
                failed[idx] = str(exc)
        return BulkResult(succeeded=succeeded, failed=failed)

    async def bulk_delete(self, ids: Sequence[uuid.UUID]) -> int:
        deleted = 0
        for id_ in ids:
            if await self.delete(id_):
                deleted += 1
        return deleted


@pytest.fixture
def widget_repository() -> InMemoryWidgetRepository:
    return InMemoryWidgetRepository()


@pytest.fixture
def make_widget():
    def _make(**overrides: Any) -> Widget:
        defaults: dict[str, Any] = {"name": "test-widget", "quantity": 1}
        defaults.update(overrides)
        return Widget(**defaults)

    return _make
