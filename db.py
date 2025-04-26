# db.py

import sqlite3

DB_PATH = "rss_reader.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
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
            published  TEXT,          -- now ISO format!
            read       INTEGER DEFAULT 0
        );
        """
        )
        conn.commit()


def add_feed(url, title=None):
    with get_conn() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO feeds (url, title) VALUES (?, ?)",
            (url, title or url),
        )
        conn.commit()


def remove_feed(url):
    with get_conn() as conn:
        cur = conn.execute("SELECT id FROM feeds WHERE url = ?", (url,))
        row = cur.fetchone()
        if not row:
            return
        feed_id = row["id"]
        conn.execute("DELETE FROM entries WHERE feed_id = ?", (feed_id,))
        conn.execute("DELETE FROM feeds WHERE id = ?", (feed_id,))
        conn.commit()


def get_feeds():
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM feeds").fetchall()
    return [dict(r) for r in rows]


def add_entry(entry_id, feed_id, title, link, published):
    with get_conn() as conn:
        conn.execute(
            """INSERT OR IGNORE INTO entries
               (id, feed_id, title, link, published)
               VALUES (?, ?, ?, ?, ?)""",
            (entry_id, feed_id, title, link, published),
        )
        conn.commit()


def get_unread_entries():
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT e.id, e.title, e.link, e.published, f.url AS feed_url
              FROM entries e
              JOIN feeds f ON e.feed_id = f.id
             WHERE e.read = 0
             ORDER BY e.published DESC
        """
        ).fetchall()
    return [dict(r) for r in rows]


def mark_entry_read(entry_id):
    with get_conn() as conn:
        conn.execute("UPDATE entries SET read = 1 WHERE id = ?", (entry_id,))
        conn.commit()
