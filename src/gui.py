"""
GUI components for RSS Reader.

This module contains the main application window and user interface logic.
"""

import tkinter as tk
import webbrowser
from tkinter import messagebox, simpledialog, ttk
from typing import Dict, List

from .feeds import (
    get_entry_link,
    get_entry_title,
    load_saved_feeds,
    parse_feed,
    save_saved_feeds,
)


class RSSReader(tk.Tk):
    """Main RSS Reader application window."""

    def __init__(self):
        super().__init__()
        self.title("RSS Reader")
        self.geometry("600x400")

        # Load title→URL mapping
        self.feeds: Dict[str, str] = load_saved_feeds()
        self.entries: List = []

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the user interface components."""
        # Top frame with controls
        top = ttk.Frame(self)
        top.pack(fill="x", padx=10, pady=5)

        # Feed selection combobox
        self.title_var = tk.StringVar(value=next(iter(self.feeds)))
        self.combo = ttk.Combobox(
            top, textvariable=self.title_var, values=list(self.feeds.keys())
        )
        self.combo.pack(side="left", fill="x", expand=True)

        # Control buttons
        fetch_btn = ttk.Button(top, text="Fetch", command=self.fetch_feed)
        fetch_btn.pack(side="left", padx=(5, 0))

        save_btn = ttk.Button(top, text="Save", command=self.save_current_feed)
        save_btn.pack(side="left", padx=(5, 0))

        # Listbox for feed entries
        self.listbox = tk.Listbox(self)
        self.listbox.pack(fill="both", expand=True, padx=10, pady=5)
        self.listbox.bind("<Double-1>", self.open_entry)

    def fetch_feed(self) -> None:
        """Fetch and display entries from the selected RSS feed."""
        # Lookup URL by the selected title
        title = self.title_var.get()
        url = self.feeds.get(title)

        if not url:
            messagebox.showwarning(
                "No Feed Selected",
                "Please select or enter a valid feed title.",
            )
            return

        # Parse the feed
        feed = parse_feed(url)
        if feed.bozo:
            messagebox.showerror(
                "Fetch Error", f"Could not parse feed:\n{feed.bozo_exception}"
            )
            return

        # Populate the listbox with entries
        self.listbox.delete(0, tk.END)
        self.entries = feed.entries

        for entry in self.entries:
            title = get_entry_title(entry)
            self.listbox.insert(tk.END, title)

    def save_current_feed(self) -> None:
        """Save a new feed URL with a custom title."""
        # Ask for feed URL and title
        url = simpledialog.askstring(
            "Feed URL", "Enter feed URL:", initialvalue=""
        )
        title = simpledialog.askstring(
            "Feed Title",
            'Give this feed a name (e.g. "My Blog"):',
            initialvalue="",
        )

        if not url or not title:
            return

        # Save the feed
        self.feeds[title] = url
        save_saved_feeds(self.feeds)

        # Update the UI
        self.combo["values"] = list(self.feeds.keys())
        self.title_var.set(title)
        messagebox.showinfo("Saved", f'Feed "{title}" saved.')

    def open_entry(self, _) -> None:
        """Open the selected feed entry in the default browser."""
        selection = self.listbox.curselection()
        if not selection:
            return

        entry = self.entries[selection[0]]
        link = get_entry_link(entry)

        if link:
            webbrowser.open(link)
        else:
            messagebox.showwarning(
                "No Link", "This entry doesn't have a link available."
            )
