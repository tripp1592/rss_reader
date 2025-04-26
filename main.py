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
    QMessageBox,
    QDialog,
    QMenu,
)
from PyQt6.QtCore import Qt, QPoint

from db import (
    init_db,
    add_feed,
    remove_feed,
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

        # Manage Feeds button
        btn_manage = QPushButton("Manage Feeds")
        btn_manage.clicked.connect(self.manage_feeds_dialog)
        layout.addWidget(btn_manage)

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

        # Left: list of unread titles
        self.list_widget = QListWidget()
        self.list_widget.setWordWrap(True)
        self.list_widget.itemClicked.connect(self.display_entry)
        splitter.addWidget(self.list_widget)

        # Right: detail pane
        self.text_browser = QTextBrowser()
        self.text_browser.anchorClicked.connect(
            lambda url: webbrowser.open(url.toString())
        )
        splitter.addWidget(self.text_browser)

        # Make left pane twice as wide as right by default
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)

    def manage_feeds_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Manage Feeds")
        dlg_layout = QVBoxLayout(dialog)

        feed_list = QListWidget()
        for f in get_feeds():
            feed_list.addItem(f["url"])

        # Enable right-click context menu
        feed_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        feed_list.customContextMenuRequested.connect(
            lambda pos: self._show_feed_context_menu(feed_list, pos)
        )

        dlg_layout.addWidget(feed_list)

        btn_close = QPushButton("Close")
        btn_close.clicked.connect(dialog.accept)
        dlg_layout.addWidget(btn_close)

        dialog.exec()

    def _show_feed_context_menu(self, feed_list: QListWidget, pos: QPoint):
        item = feed_list.itemAt(pos)
        if not item:
            return

        menu = QMenu(feed_list)
        remove_action = menu.addAction("Remove Feed")
        chosen = menu.exec(feed_list.mapToGlobal(pos))

        if chosen == remove_action:
            url = item.text()
            confirm = QMessageBox.question(
                self,
                "Confirm Remove",
                f"Remove feed:\n{url} ?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if confirm == QMessageBox.StandardButton.Yes:
                remove_feed(url)
                feed_list.takeItem(feed_list.row(item))
                self.fetch_and_show()

    def add_feed_dialog(self):
        url, ok = QInputDialog.getText(self, "Subscribe to a new feed", "Feed URL:")
        if ok and url.strip():
            add_feed(url.strip())
            self.fetch_and_show()

    def fetch_and_show(self):
        # fetch & store
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

        # display unread
        unread = get_unread_entries()
        self.list_widget.clear()
        for ent in unread:
            raw = ent.get("title", "")
            display_title = " ".join(raw.split()) or ent.get("link", "")
            item = QListWidgetItem(display_title)
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
