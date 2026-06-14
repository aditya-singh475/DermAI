"""SQLite database management with proper connection handling."""

import sqlite3
import logging
from contextlib import contextmanager
from datetime import datetime, timezone

from .config import get_settings

logger = logging.getLogger(__name__)


def _get_db_path() -> str:
    return get_settings().DATABASE_URL


def _migrate_predictions_table(conn: sqlite3.Connection):
    """Add columns to existing databases without breaking old installs."""
    columns = {
        row[1] for row in conn.execute("PRAGMA table_info(predictions)").fetchall()
    }
    if "image_path" not in columns:
        conn.execute("ALTER TABLE predictions ADD COLUMN image_path TEXT")
    if "risk_level" not in columns:
        conn.execute("ALTER TABLE predictions ADD COLUMN risk_level TEXT")


def init_db():
    """Initialize database tables."""
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                filename TEXT NOT NULL,
                predicted_class TEXT NOT NULL,
                confidence REAL NOT NULL,
                all_probabilities TEXT,
                image_path TEXT,
                risk_level TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (username) REFERENCES users (username)
            )
        """)
        _migrate_predictions_table(conn)
        conn.commit()
    logger.info("Database initialized successfully")


@contextmanager
def get_db():
    """Context manager for database connections — one connection per request."""
    conn = sqlite3.connect(_get_db_path())
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()
