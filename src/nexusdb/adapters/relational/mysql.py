"""MySQL adapter. DSNs should use the ``mysql+asyncmy://`` scheme."""

from __future__ import annotations

from nexusdb.adapters.relational.base import SQLAlchemyAdapter
from nexusdb.core.enums import DatabaseKind
from nexusdb.factory.db_factory import register_adapter


class MySQLAdapter(SQLAlchemyAdapter):
    kind = DatabaseKind.MYSQL


register_adapter(DatabaseKind.MYSQL, MySQLAdapter)

__all__ = ["MySQLAdapter"]
