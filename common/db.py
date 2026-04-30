import logging
from contextlib import contextmanager

from django.db import connection, OperationalError, DatabaseError as DjangoDatabaseError

from common.exceptions import DatabaseError

logger = logging.getLogger(__name__)


@contextmanager
def get_cursor():
    """Yields a DB cursor and converts all DB errors into DatabaseError."""
    try:
        with connection.cursor() as cursor:
            yield cursor
    except (OperationalError, DjangoDatabaseError) as exc:
        logger.error("Database error: %s", exc, exc_info=True)
        raise DatabaseError("A database error occurred") from exc


def execute_query(sql: str, params: tuple | list | None = None) -> list[dict]:
    """Execute a SELECT and return rows as a list of dicts."""
    with get_cursor() as cursor:
        cursor.execute(sql, params or [])
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def execute_one(sql: str, params: tuple | list | None = None) -> dict | None:
    """Execute a SELECT and return the first row as a dict, or None."""
    with get_cursor() as cursor:
        cursor.execute(sql, params or [])
        if cursor.description is None:
            return None
        columns = [col[0] for col in cursor.description]
        row = cursor.fetchone()
        return dict(zip(columns, row)) if row else None


def execute_write(sql: str, params: tuple | list | None = None) -> int:
    """Execute an INSERT/UPDATE/DELETE and return affected row count."""
    with get_cursor() as cursor:
        cursor.execute(sql, params or [])
        return cursor.rowcount


def execute_write_returning(sql: str, params: tuple | list | None = None) -> dict | None:
    """Execute an INSERT/UPDATE with RETURNING clause and return the row as a dict."""
    with get_cursor() as cursor:
        cursor.execute(sql, params or [])
        if cursor.description is None:
            return None
        columns = [col[0] for col in cursor.description]
        row = cursor.fetchone()
        return dict(zip(columns, row)) if row else None
