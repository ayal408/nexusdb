"""nexusdb: a unified, enterprise-grade multi-database interface for Python.

Public surface is re-exported here so application code can do::

    from nexusdb import AbstractRepository, ConnectionConfig, DatabaseFactory, NexusDBError
"""

from __future__ import annotations

from nexusdb.core import exception_mapper as _exception_mapper  # noqa: F401  (bootstraps mappers)
from nexusdb.core.config import (
    CircuitBreakerConfig,
    ConnectionConfig,
    NexusDBSettings,
    NodeConfig,
    PoolConfig,
    RetryConfig,
)
from nexusdb.core.context import correlation_scope, get_correlation_id, tenant_scope
from nexusdb.core.enums import DatabaseKind, HealthStatus, RoutingRole
from nexusdb.core.exceptions import (
    BulkOperationError,
    NexusDBError,
    RecordNotFoundError,
    TenantContextMissingError,
)
from nexusdb.core.logging import configure_logging, get_logger
from nexusdb.factory.db_factory import DatabaseFactory, register_adapter
from nexusdb.interfaces.adapter import AbstractDatabaseAdapter, HealthCheckResult
from nexusdb.interfaces.cache import AbstractCache, cache_aside
from nexusdb.interfaces.events import AbstractEventDispatcher, AbstractOutboxStore, DomainEvent
from nexusdb.interfaces.repository import AbstractRepository, BulkResult, Page, SortSpec
from nexusdb.interfaces.unit_of_work import AbstractUnitOfWork
from nexusdb.models.base import AuditRecord, Entity

__version__ = "0.1.0"

__all__ = [
    "__version__",
    # config / settings
    "ConnectionConfig",
    "NexusDBSettings",
    "NodeConfig",
    "PoolConfig",
    "RetryConfig",
    "CircuitBreakerConfig",
    # context
    "correlation_scope",
    "get_correlation_id",
    "tenant_scope",
    # enums
    "DatabaseKind",
    "HealthStatus",
    "RoutingRole",
    # exceptions
    "NexusDBError",
    "RecordNotFoundError",
    "BulkOperationError",
    "TenantContextMissingError",
    # logging
    "configure_logging",
    "get_logger",
    # factory
    "DatabaseFactory",
    "register_adapter",
    # interfaces
    "AbstractDatabaseAdapter",
    "HealthCheckResult",
    "AbstractCache",
    "cache_aside",
    "AbstractEventDispatcher",
    "AbstractOutboxStore",
    "DomainEvent",
    "AbstractRepository",
    "BulkResult",
    "Page",
    "SortSpec",
    "AbstractUnitOfWork",
    # models
    "Entity",
    "AuditRecord",
]
