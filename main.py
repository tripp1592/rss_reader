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
    QInputDialog,
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
# Seed feed URLs for first run
DEFAULT_FEEDS = [
    "https://xkcd.com/rss.xml",
    "https://hnrss.org/frontpage",
    "https://www.govinfo.gov/rss/fr.xml",
]
# ----------------------------------------


class RSSReaderGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        # 1) ensure our database + feeds table exist
        init_db()
        # 2) insert any default feeds on first run
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

        # Add Feed button
        btn_add = QPushButton("Add Feed")
        btn_add.clicked.connect(self.add_feed_dialog)
        layout.addWidget(btn_add)

        # Refresh button
        btn_refresh = QPushButton("Refresh")
        btn_refresh.clicked.connect(self.fetch_and_show)
        layout.addWidget(btn_refresh)

        # Splitter between list and detail
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)

        # List widget for unread entry titles
        self.list_widget = QListWidget()
        # allow word-wrap so long titles wrap onto multiple lines
        self.list_widget.setWordWrap(True)
        splitter.addWidget(self.list_widget)

        # Detail pane for title, link, summary, etc.
        self.text_browser = QTextBrowser()
        self.text_browser.anchorClicked.connect(
            lambda url: webbrowser.open(url.toString())
        )
        splitter.addWidget(self.text_browser)

        # Bias splitter so left pane is twice the width of right
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)

        # connect click handler after list_widget exists
        self.list_widget.itemClicked.connect(self.display_entry)

    def add_feed_dialog(self):
        url, ok = QInputDialog.getText(self, "Subscribe to a new feed", "Feed URL:")
        if ok and url.strip():
            add_feed(url.strip())
            self.fetch_and_show()

    def fetch_and_show(self):
        # 1) fetch each feed and store new entries in the DB
        for feed in get_feeds():
            parsed = feedparser.parse(feed["url"])
            for entry in parsed.entries:
                entry_id = entry.get("id") or (entry.link + entry.get("published", ""))
                add_entry(
                    entry_id,
                    feed["id"],
                    entry.get("title", ""),
                    entry.link,
                    entry.get("published", ""),
                )

        # 2) load all unread entries
        unread = get_unread_entries()
        self.list_widget.clear()

        for ent in unread:
            # normalize whitespace in the title to collapse newlines/indentation
            raw = ent.get("title", "")
            display_title = " ".join(raw.split()) or ent.get("link", "")
            item = QListWidgetItem(display_title)
            # store the full entry dict for detail pane & marking read
            item.setData(Qt.ItemDataRole.UserRole, ent)
            self.list_widget.addItem(item)

        if not unread:
            self.text_browser.setHtml("<p><i>No new items.</i></p>")

    def display_entry(self, item: QListWidgetItem):
        ent = item.data(Qt.ItemDataRole.UserRole)
        title = ent.get("title", "<i>(no title)</i>")
        link = ent.get("link", "")
        pub = ent.get("published", "")
        html = (
            f"<h2>{title}</h2>"
            f"<p><a href='{link}'>{link}</a></p>"
            f"<p><i>Published: {pub}</i></p>"
        )
        self.text_browser.setHtml(html)
        mark_entry_read(ent["id"])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RSSReaderGUI()
    window.show()
    sys.exit(app.exec())
