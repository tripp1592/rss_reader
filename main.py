#!/usr/bin/env python3
# main.py

import sys
import webbrowser
import feedparser

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QTextBrowser,
    QSplitter,
)
from PyQt6.QtCore import Qt

from db import (
    init_db,
    add_feed,
    get_feeds,
    add_entry,
    get_unread_entries,
    mark_entry_read,
)

# ----------------------------------------
# Seed URLs you want to subscribe to here:
DEFAULT_FEEDS = [
    "https://xkcd.com/rss.xml",
    "https://hnrss.org/frontpage",
]
# ----------------------------------------


class RSSReaderGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        # Ensure our database and feeds table exist
        init_db()
        for url in DEFAULT_FEEDS:
            add_feed(url)

        self.init_ui()
        self.fetch_and_show()

    def init_ui(self):
        self.setWindowTitle("My PyQt6 RSS Reader")
        self.resize(800, 600)

        container = QWidget()
        self.setCentralWidget(container)
        layout = QVBoxLayout(container)

        # Refresh button
        btn_refresh = QPushButton("Refresh")
        btn_refresh.clicked.connect(self.fetch_and_show)
        layout.addWidget(btn_refresh)

        # Splitter: list on left, content on right
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)

        # List of unread entries
        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self.display_entry)
        splitter.addWidget(self.list_widget)

        # Viewer for selected entry
        self.text_browser = QTextBrowser()
        # Make links clickable
        self.text_browser.anchorClicked.connect(
            lambda url: webbrowser.open(url.toString())
        )
        splitter.addWidget(self.text_browser)

    def fetch_and_show(self):
        # 1) Fetch each feed and store any new entries
        for feed in get_feeds():
            parsed = feedparser.parse(feed["url"])
            for entry in parsed.entries:
                entry_id = entry.get("id") or (entry.link + entry.get("published", ""))
                add_entry(
                    entry_id,
                    feed["id"],
                    entry.title,
                    entry.link,
                    entry.get("published", ""),
                )

        # 2) Load unread entries and populate the list
        unread = get_unread_entries()
        self.list_widget.clear()

        for ent in unread:
            # Show title and which feed it came from
            item = QListWidgetItem(f"{ent['title']}  ({ent['feed_url']})")
            # Store the entry ID for marking as read later
            item.setData(Qt.ItemDataRole.UserRole, ent["id"])
            self.list_widget.addItem(item)

        if not unread:
            self.text_browser.setHtml("<p><i>No new items.</i></p>")

    def display_entry(self, item: QListWidgetItem):
        entry_id = item.data(Qt.ItemDataRole.UserRole)
        # Retrieve the entry data from the DB if needed,
        # or embed additional metadata in the UserRole data.
        # For simplicity, we'll just show link and title:
        # (You can extend this to show summaries, dates, etc.)
        html = (
            f"<h2>{item.text()}</h2>"
            f"<p><a href='{item.text().split('(')[0].strip()}'>{item.text().split('(')[0].strip()}</a></p>"
        )
        self.text_browser.setHtml(html)

        # Mark this entry as read so it won't show up next time
        mark_entry_read(entry_id)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RSSReaderGUI()
    window.show()
    sys.exit(app.exec())
