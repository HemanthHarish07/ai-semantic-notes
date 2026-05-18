import os
import traceback
from sqlalchemy import text


def _is_postgres_url(url: str | None) -> bool:
    return bool(url) and url.startswith("postgres")


def pgvector_capabilities(database_url: str | None) -> dict:
    """Best-effort runtime detection.

    Returns:
      {
        "pgvector_available": bool,
        "using_pgvector": bool,
        "reason": str
      }

    Never raises.
    """
    if not _is_postgres_url(database_url):
        return {
            "pgvector_available": False,
            "using_pgvector": False,
            "reason": "DATABASE_URL is not Postgres",
        }

    # Import pgvector driver only when running under Postgres.
    try:
        import pgvector  # noqa: F401
    except Exception:
        return {
            "pgvector_available": False,
            "using_pgvector": False,
            "reason": "pgvector package not installed",
        }

    # Try to check extension exists. We do it in a best-effort manner.
    # We do not have a connection here; actual check can be done by endpoint.
    return {
        "pgvector_available": True,
        "using_pgvector": True,
        "reason": "Postgres URL + pgvector package present",
    }


def ensure_pgvector_extension(connection) -> bool:
    """Ensures vector extension exists in current DB.

    Returns True if extension exists or created, False otherwise.
    Never raises.
    """
    try:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        return True
    except Exception:
        traceback.print_exc()
        return False

