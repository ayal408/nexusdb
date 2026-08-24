"""Generic repository contract shared by relational, document, and vector stores.

Concrete repositories are parameterized on a Pydantic model (the domain
entity) and an id type, giving callers full static typing:

    class UserRepository(AbstractRepository[User, UUID]): ...

Every mutating method accepts an optional ``idempotency_key``; adapters that
can enforce it natively (e.g. via a unique constraint on the key) should, and
the Unit of Work provides a generic fallback (see
:mod:`nexusdb.interfaces.unit_of_work`).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

TModel = TypeVar("TModel", bound=BaseModel)
TId = TypeVar("TId")


class SortSpec(BaseModel):
    """One field to sort by; repositories combine a list of these for multi-key sort."""

    model_config = ConfigDict(frozen=True)

    field: str
    descending: bool = False


class Page(BaseModel, Generic[TModel]):
    """A page of results plus enough metadata to fetch the next one."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    items: list[TModel]
    total: int | None = Field(default=None, description="Total matches, if the backend computed it cheaply")
    limit: int
    offset: int

    @property
    def has_more(self) -> bool:
        return self.total is not None and self.offset + len(self.items) < self.total


class BulkResult(BaseModel, Generic[TModel]):
    """Outcome of a bulk operation, supporting partial success."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    succeeded: list[TModel] = Field(default_factory=list)
    failed: dict[int, str] = Field(default_factory=dict, description="index -> error message")

    @property
    def success_count(self) -> int:
        return len(self.succeeded)

    @property
    def failure_count(self) -> int:
        return len(self.failed)

    @property
    def all_succeeded(self) -> bool:
        return not self.failed


class AbstractRepository(ABC, Generic[TModel, TId]):
    """CRUD + bulk + query contract implemented once per (model, backend) pair."""

    model: type[TModel]

    # -- single-item CRUD ----------------------------------------------------

    @abstractmethod
    async def get_by_id(self, id_: TId) -> TModel | None:
        """Return the entity, or ``None`` if it does not exist (never raises for a miss)."""

    async def get_by_id_or_raise(self, id_: TId) -> TModel:
        entity = await self.get_by_id(id_)
        if entity is None:
            from nexusdb.core.exceptions import RecordNotFoundError

            raise RecordNotFoundError(self.model.__name__, id_)
        return entity

    @abstractmethod
    async def create(self, entity: TModel, *, idempotency_key: str | None = None) -> TModel:
        """Persist a new entity, returning it with any backend-assigned fields populated."""

    @abstractmethod
    async def update(self, id_: TId, changes: Mapping[str, Any]) -> TModel:
        """Apply a partial update and return the resulting entity."""

    @abstractmethod
    async def delete(self, id_: TId) -> bool:
        """Delete by id; returns ``True`` if a record was actually removed."""

    # -- querying -------------------------------------------------------------

    @abstractmethod
    async def find(
        self,
        criteria: Mapping[str, Any] | None = None,
        *,
        limit: int = 50,
        offset: int = 0,
        sort: Sequence[SortSpec] | None = None,
    ) -> Page[TModel]:
        """Query by an equality-filter mapping (adapters may extend with richer operators)."""

    @abstractmethod
    async def count(self, criteria: Mapping[str, Any] | None = None) -> int:
        ...

    async def exists(self, criteria: Mapping[str, Any] | None = None) -> bool:
        return await self.count(criteria) > 0

    # -- bulk operations --------------------------------------------------------

    @abstractmethod
    async def bulk_create(
        self, entities: Sequence[TModel], *, idempotency_key: str | None = None
    ) -> BulkResult[TModel]:
        ...

    @abstractmethod
    async def bulk_update(self, updates: Mapping[TId, Mapping[str, Any]]) -> BulkResult[TModel]:
        ...

    @abstractmethod
    async def bulk_delete(self, ids: Sequence[TId]) -> int:
        """Returns the number of records actually deleted."""


__all__ = ["AbstractRepository", "BulkResult", "Page", "SortSpec", "TId", "TModel"]
