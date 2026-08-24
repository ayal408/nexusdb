from nexusdb.interfaces.adapter import AbstractDatabaseAdapter, HealthCheckResult
from nexusdb.interfaces.cache import AbstractCache
from nexusdb.interfaces.events import AbstractEventDispatcher, AbstractOutboxStore, DomainEvent
from nexusdb.interfaces.repository import AbstractRepository, BulkResult, Page, SortSpec
from nexusdb.interfaces.unit_of_work import AbstractUnitOfWork

__all__ = [
    "AbstractCache",
    "AbstractDatabaseAdapter",
    "AbstractEventDispatcher",
    "AbstractOutboxStore",
    "AbstractRepository",
    "AbstractUnitOfWork",
    "BulkResult",
    "DomainEvent",
    "HealthCheckResult",
    "Page",
    "SortSpec",
]
