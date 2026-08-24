"""SQLite adapter. DSNs should use the ``sqlite+aiosqlite://`` scheme.

SQLite has no concept of replicas; a config with a REPLICA node still works
(the base adapter simply routes reads to it), but in practice SQLite
deployments should configure a single MASTER node only.
"""

from __future__ import annotations

from nexusdb.adapters.relational.base import SQLAlchemyAdapter
from nexusdb.core.enums import DatabaseKind
from nexusdb.factory.db_factory import register_adapter


class SQLiteAdapter(SQLAlchemyAdapter):
    kind = DatabaseKind.SQLITE


register_adapter(DatabaseKind.SQLITE, SQLiteAdapter)

__all__ = ["SQLiteAdapter"]
