# db.py
import sqlite3
from datetime import datetime

DB_PATH = "rss_reader.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if they don't exist."""
    with get_conn() as conn:
        conn.executescript(
            """
        CREATE TABLE IF NOT EXISTS feeds (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            url      TEXT    UNIQUE NOT NULL,
            title    TEXT
        );
        CREATE TABLE IF NOT EXISTS entries (
            id         TEXT    PRIMARY KEY,
            feed_id    INTEGER NOT NULL REFERENCES feeds(id),
            title      TEXT,
            link       TEXT,
            published  TEXT,
            read       INTEGER DEFAULT 0
        );
        """
        )
        conn.commit()


def add_feed(url, title=None):
    """Insert a new feed (or ignore if exists)."""
    with get_conn() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO feeds (url, title) VALUES (?, ?)",
            (url, title or url),
        )
        conn.commit()


def get_feeds():
    """Return list of feeds as dicts."""
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM feeds").fetchall()
    return [dict(row) for row in rows]


def add_entry(entry_id, feed_id, title, link, published):
    """Insert new entry if it isn't already in the DB."""
    with get_conn() as conn:
        conn.execute(
            """INSERT OR IGNORE INTO entries
               (id, feed_id, title, link, published)
               VALUES (?, ?, ?, ?, ?)""",
            (entry_id, feed_id, title, link, published),
        )
        conn.commit()


def get_unread_entries():
    """Return all unread entries, newest first."""
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT e.id, e.title, e.link, e.published, f.url AS feed_url
               FROM entries e
               JOIN feeds f ON e.feed_id = f.id
               WHERE e.read = 0
               ORDER BY datetime(e.published) DESC"""
        ).fetchall()
    return [dict(r) for r in rows]


def mark_entry_read(entry_id):
    """Mark an entry as read."""
    with get_conn() as conn:
        conn.execute("UPDATE entries SET read = 1 WHERE id = ?", (entry_id,))
        conn.commit()
