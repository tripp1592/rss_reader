#!/usr/bin/env python3
# main.py

import sys
import webbrowser
import feedparser
from email.utils import parsedate_to_datetime
from datetime import datetime

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


class RSSReaderGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        init_db()
        self.init_ui()
        self.fetch_and_show()

    def init_ui(self):
        self.setWindowTitle("My PyQt6 RSS Reader")
        self.resize(800, 600)
        container = QWidget()
        self.setCentralWidget(container)
        layout = QVBoxLayout(container)

        btn_manage = QPushButton("Manage Feeds")
        btn_manage.clicked.connect(self.manage_feeds_dialog)
        layout.addWidget(btn_manage)

        btn_add = QPushButton("Add Feed")
        btn_add.clicked.connect(self.add_feed_dialog)
        layout.addWidget(btn_add)

        btn_refresh = QPushButton("Refresh")
        btn_refresh.clicked.connect(self.fetch_and_show)
        layout.addWidget(btn_refresh)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)

        self.list_widget = QListWidget()
        self.list_widget.setWordWrap(True)
        self.list_widget.itemClicked.connect(self.display_entry)
        splitter.addWidget(self.list_widget)

        self.text_browser = QTextBrowser()
        self.text_browser.anchorClicked.connect(
            lambda url: webbrowser.open(url.toString())
        )
        splitter.addWidget(self.text_browser)

        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)

    def manage_feeds_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Manage Feeds")
        dlg_layout = QVBoxLayout(dialog)
        feed_list = QListWidget()
        for f in sorted(get_feeds(), key=lambda x: x["id"], reverse=True):
            feed_list.addItem(f["url"])
        feed_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        feed_list.customContextMenuRequested.connect(
            lambda pos: self._show_feed_context_menu(feed_list, pos)
        )
        dlg_layout.addWidget(feed_list)
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(dialog.accept)
        dlg_layout.addWidget(btn_close)
        dialog.exec()

    def _show_feed_context_menu(self, feed_list, pos):
        item = feed_list.itemAt(pos)
        if not item:
            return
        menu = QMenu(feed_list)
        remove = menu.addAction("Remove Feed")
        if menu.exec(feed_list.mapToGlobal(pos)) == remove:
            url = item.text()
            if (
                QMessageBox.question(
                    self,
                    "Confirm Remove",
                    f"Remove feed:\n{url} ?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                )
                == QMessageBox.StandardButton.Yes
            ):
                remove_feed(url)
                feed_list.takeItem(feed_list.row(item))
                self.fetch_and_show()

    def add_feed_dialog(self):
        url, ok = QInputDialog.getText(self, "Subscribe to a new feed", "Feed URL:")
        if ok and url.strip():
            add_feed(url.strip())
            self.fetch_and_show()

    def fetch_and_show(self):
        # 1) fetch & store with ISO dates
        for feed in get_feeds():
            parsed = feedparser.parse(feed["url"])
            for entry in parsed.entries:
                eid = entry.get("id") or (entry.link + entry.get("published", ""))
                pub_raw = entry.get("published", "")
                try:
                    dt = parsedate_to_datetime(pub_raw)
                    pub_iso = dt.isoformat()
                except Exception:
                    pub_iso = ""
                add_entry(eid, feed["id"], entry.get("title", ""), entry.link, pub_iso)

        # 2) retrieve unread
        unread = (
            get_unread_entries()
        )  # :contentReference[oaicite:4]{index=4}&#8203;:contentReference[oaicite:5]{index=5}

        # 3) Python-side sort by ISO timestamp
        def parse_iso(s):
            try:
                return datetime.fromisoformat(s)
            except:
                return datetime.min

        unread.sort(key=lambda e: parse_iso(e["published"]), reverse=True)

        # 4) populate list
        self.list_widget.clear()
        for ent in unread:
            raw = ent.get("title", "")
            disp = " ".join(raw.split()) or ent.get("link", "")
            item = QListWidgetItem(disp)
            item.setData(Qt.ItemDataRole.UserRole, ent)
            self.list_widget.addItem(item)
        if not unread:
            self.text_browser.setHtml("<p><i>No new items.</i></p>")

    def display_entry(self, item):
        ent = item.data(Qt.ItemDataRole.UserRole)
        html = (
            f"<h2>{ent.get('title','<i>(no title)</i>')}</h2>"
            f"<p><a href='{ent.get('link','')}'>{ent.get('link','')}</a></p>"
            f"<p><i>Published: {ent.get('published','')}</i></p>"
        )
        self.text_browser.setHtml(html)
        mark_entry_read(ent["id"])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = RSSReaderGUI()
    win.show()
    sys.exit(app.exec())
