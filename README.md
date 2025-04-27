# My PyQt6 RSS Reader

A simple desktop RSS reader built with PyQt6 and SQLite.  
Fetches feeds, stores entries with ISO-8601 timestamps, and lets you add/remove/manage subscriptions at runtime.


## Features

- **Add Feed**  
  Subscribe to any RSS/Atom URL via the GUI.

- **Manage Feeds**  
  Click **Manage Feeds**, right-click any feed URL to remove it (with confirmation).

- **Automatic Fetch & Store**  
  On **Refresh**, downloads all items, stores new ones in an SQLite database, and marks read/unread.

- **ISO-8601 Timestamps & Sorting**  
  Entry `pubDate` strings are parsed into ISO-8601 format before storage.  
  Entries are listed newest→oldest automatically.

- **Read/Unread Tracking**  
  Clicking an item marks it as read and removes it from the unread list.

- **Detail View**  
  Three-pane interface:  
  - **Left**: List of unread titles (word-wrapped)  
  - **Right**: Detail pane with full title, link, and published date.

---

## Installation

1. **Clone this repo**  
   ```bash
   git clone https://github.com/yourusername/rss-reader-pyqt6.git
   cd rss-reader-pyqt6
   ```

2. **Create & activate a virtualenv**  
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # Linux/macOS
   venv\Scripts\activate      # Windows
   ```

3. **Install dependencies**  
   ```bash
   pip install PyQt6 feedparser
   ```

---

## Usage

1. **Initialize the database**  
   On first run, the app will create `rss_reader.db` with the required tables.

2. **Run the app**  
   ```bash
   python main.py
   ```

3. **Subscribe to feeds**  
   - Click **Add Feed**, paste a feed URL, and hit **OK**.
   - Or click **Manage Feeds** → right-click an existing URL for removal.

4. **Fetch & view items**  
   - Click **Refresh** to pull the latest entries.  
   - Unread items appear in the left list; click one to see details (and mark it as read).

---

## Project Structure

```
.
├── main.py       # PyQt6 GUI & application logic
├── db.py         # SQLite helpers: init, add/remove feeds, add entries, queries
├── rss_reader.db # (generated) SQLite database file
└── README.md     # This file
```

---

## Notes & Tips

- **Database file**  
  `rss_reader.db` lives in the same directory as `main.py`. Back it up or copy it to migrate your subscriptions and history.

- **Date parsing**  
  Uses Python’s `email.utils.parsedate_to_datetime` to convert feed `pubDate` into ISO strings for reliable SQL sorting.

- **Word-wrap**  
  Long titles wrap in the list view—no horizontal scrolling needed.

- **Extending**  
  - Add support for folders/tags by extending the `feeds` table.  
  - Integrate desktop notifications (`win10toast`) for high-priority feeds.  
  - Implement search/filter in the GUI.

