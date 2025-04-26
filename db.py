# db.py

import sqlite3

DB_PATH = "rss_reader.db"


def get_conn():
    """Open a connection to the SQLite database with row access by name."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create the feeds and entries tables if they don't already exist."""
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
    """Insert a new feed URL (ignoring if already present)."""
    with get_conn() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO feeds (url, title) VALUES (?, ?)",
            (url, title or url),
        )
        conn.commit()


def remove_feed(url):
    """Delete a feed and all its entries by URL."""
    with get_conn() as conn:
        # find feed id
        cur = conn.execute("SELECT id FROM feeds WHERE url = ?", (url,))
        row = cur.fetchone()
        if not row:
            return
        feed_id = row["id"]

        # delete entries belonging to that feed
        conn.execute("DELETE FROM entries WHERE feed_id = ?", (feed_id,))

        # delete the feed itself
        conn.execute("DELETE FROM feeds WHERE id = ?", (feed_id,))
        conn.commit()


def get_feeds():
    """Return a list of all feeds as dicts with keys 'id', 'url', 'title'."""
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM feeds").fetchall()
    return [dict(r) for r in rows]


def add_entry(entry_id, feed_id, title, link, published):
    """
    Insert a new entry if it doesn't already exist.
    entry_id should be globally unique (e.g. GUID or link+timestamp).
    """
    with get_conn() as conn:
        conn.execute(
            """INSERT OR IGNORE INTO entries
               (id, feed_id, title, link, published)
               VALUES (?, ?, ?, ?, ?)""",
            (entry_id, feed_id, title, link, published),
        )
        conn.commit()


def get_unread_entries():
    """
    Return all unread entries (read = 0), newest first,
    each as a dict including the originating feed's URL.
    """
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT e.id, e.title, e.link, e.published, f.url AS feed_url
              FROM entries e
              JOIN feeds f ON e.feed_id = f.id
             WHERE e.read = 0
             ORDER BY datetime(e.published) DESC
        """
        ).fetchall()
    return [dict(r) for r in rows]


def mark_entry_read(entry_id):
    """Mark the given entry as read so it no longer appears in unread queries."""
    with get_conn() as conn:
        conn.execute("UPDATE entries SET read = 1 WHERE id = ?", (entry_id,))
        conn.commit()
