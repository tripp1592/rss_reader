# main.py (excerpt)

import json
import os
import tkinter as tk
import webbrowser
from tkinter import messagebox, ttk, simpledialog

import feedparser

FEEDS_FILE = "feeds.json"
DEFAULT_FEEDS = {
    "Google News": "https://news.google.com/rss",
    "Modern Wisdom": "https://podcasts.apple.com/gb/feed/podcast/modern-wisdom/id1347973549/rss",
}


def load_saved_feeds():
    """Load dict of {title: url} from JSON, or fall back to DEFAULT_FEEDS."""
    if os.path.exists(FEEDS_FILE):
        try:
            with open(FEEDS_FILE, "r") as f:
                data = json.load(f)
            if isinstance(data, dict) and data:
                return data
        except (json.JSONDecodeError, IOError):
            pass
    return DEFAULT_FEEDS.copy()


def save_saved_feeds(feeds_dict):
    """Save dict of {title: url} to JSON."""
    with open(FEEDS_FILE, "w") as f:
        json.dump(feeds_dict, f, indent=2)


class RSSReader(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("RSS Reader")
        self.geometry("600x400")

        # 1) Load title→URL mapping
        self.feeds = load_saved_feeds()  # dict[str,str]

        # 2) Combobox shows only titles
        top = ttk.Frame(self)
        top.pack(fill="x", padx=10, pady=5)

        self.title_var = tk.StringVar(value=next(iter(self.feeds)))
        self.combo = ttk.Combobox(
            top, textvariable=self.title_var, values=list(self.feeds.keys())
        )
        self.combo.pack(side="left", fill="x", expand=True)

        fetch_btn = ttk.Button(top, text="Fetch", command=self.fetch_feed)
        fetch_btn.pack(side="left", padx=(5, 0))
        save_btn = ttk.Button(top, text="Save", command=self.save_current_feed)
        save_btn.pack(side="left", padx=(5, 0))

        # 3) Listbox for entries
        self.listbox = tk.Listbox(self)
        self.listbox.pack(fill="both", expand=True, padx=10, pady=5)
        self.listbox.bind("<Double-1>", self.open_entry)
        self.entries = []

    def fetch_feed(self):
        # Lookup URL by the selected title
        title = self.title_var.get()
        url = self.feeds.get(title)
        if not url:
            messagebox.showwarning(
                "No Feed Selected",
                "Please select or enter a valid feed title.",
            )
            return

        feed = feedparser.parse(url)
        if feed.bozo:
            messagebox.showerror(
                "Fetch Error", f"Could not parse feed:\n{feed.bozo_exception}"
            )
            return

        self.listbox.delete(0, tk.END)
        self.entries = feed.entries
        for e in self.entries:
            title = getattr(e, 'title', 'Untitled')
            self.listbox.insert(tk.END, str(title))

    def save_current_feed(self):
        # Ask for a friendly title for the URL
        url = simpledialog.askstring(
            "Feed URL", "Enter feed URL:", initialvalue=""
        )
        title = simpledialog.askstring(
            "Feed Title",
            "Give this feed a name (e.g. “My Blog”):",
            initialvalue="",
        )
        if not url or not title:
            return

        self.feeds[title] = url
        save_saved_feeds(self.feeds)

        # Update combobox
        self.combo["values"] = list(self.feeds.keys())
        self.title_var.set(title)
        messagebox.showinfo("Saved", f"Feed “{title}” saved.")

    def open_entry(self, _):
        idx = self.listbox.curselection()
        if not idx:
            return
        
        entry = self.entries[idx[0]]
        
        # Try to get link from the links list first, then fallback to id
        link = None
        if hasattr(entry, 'links') and entry.links:
            # Get the first link that has an href
            for link_obj in entry.links:
                if hasattr(link_obj, 'href'):
                    link = link_obj.href
                    break
        
        # Fallback to id if no link found
        if not link:
            link = getattr(entry, 'id', None)
        
        if link:
            webbrowser.open(link)
        else:
            messagebox.showwarning("No Link", "This entry doesn't have a link available.")


if __name__ == "__main__":
    app = RSSReader()
    app.mainloop()
