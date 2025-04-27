#!/usr/bin/env python3
# main.py

import sys
import webbrowser
import feedparser
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone

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

        # Left: unread titles
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

        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)

    def manage_feeds_dialog(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Manage Feeds")
        layout = QVBoxLayout(dlg)

        feed_list = QListWidget()
        for f in sorted(get_feeds(), key=lambda x: x["id"], reverse=True):
            feed_list.addItem(f["url"])
        feed_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        feed_list.customContextMenuRequested.connect(
            lambda pos: self._show_feed_context_menu(feed_list, pos)
        )
        layout.addWidget(feed_list)

        btn_close = QPushButton("Close")
        btn_close.clicked.connect(dlg.accept)
        layout.addWidget(btn_close)

        dlg.exec()

    def _show_feed_context_menu(self, feed_list: QListWidget, pos: QPoint):
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
        # 1) Fetch & store with epoch
        for feed in get_feeds():
            parsed = feedparser.parse(feed["url"])
            for entry in parsed.entries:
                eid = entry.get("id") or (entry.link + entry.get("published", ""))
                pub_raw = entry.get("published", "")
                try:
                    dt = parsedate_to_datetime(pub_raw)
                    # normalize to UTC
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=timezone.utc)
                    epoch = int(dt.timestamp())
                except Exception:
                    epoch = 0
                add_entry(eid, feed["id"], entry.get("title", ""), entry.link, epoch)

        # 2) Load & display unread (SQL now sorts by published DESC)
        unread = get_unread_entries()
        self.list_widget.clear()
        for ent in unread:
            raw = ent.get("title", "")
            title = " ".join(raw.split()) or ent.get("link", "")
            item = QListWidgetItem(title)
            item.setData(Qt.ItemDataRole.UserRole, ent)
            self.list_widget.addItem(item)

        if not unread:
            self.text_browser.setHtml("<p><i>No new items.</i></p>")

    def display_entry(self, item: QListWidgetItem):
        ent = item.data(Qt.ItemDataRole.UserRole)
        # convert epoch back to readable form
        pub_epoch = ent.get("published", 0) or 0
        try:
            dt = datetime.fromtimestamp(pub_epoch, tz=timezone.utc)
            pub_str = dt.strftime("%a, %d %b %Y %H:%M:%S %z")
        except Exception:
            pub_str = ""
        html = (
            f"<h2>{ent.get('title','<i>(no title)</i>')}</h2>"
            f"<p><a href='{ent.get('link','')}'>{ent.get('link','')}</a></p>"
            f"<p><i>Published: {pub_str}</i></p>"
        )
        self.text_browser.setHtml(html)
        mark_entry_read(ent["id"])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RSSReaderGUI()
    window.show()
    sys.exit(app.exec())
