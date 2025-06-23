# main.py

import tkinter as tk
import webbrowser
from tkinter import messagebox, ttk

import feedparser

FEED_URL = "https://news.google.com/rss"  # you can change this later


class RSSReader(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("RSS Reader")
        self.geometry("600x400")

        # 1) URL entry + Fetch button
        top_frame = ttk.Frame(self)
        top_frame.pack(fill="x", padx=10, pady=5)

        self.url_var = tk.StringVar(value=FEED_URL)
        url_entry = ttk.Entry(top_frame, textvariable=self.url_var)
        url_entry.pack(side="left", fill="x", expand=True)
        fetch_btn = ttk.Button(
            top_frame, text="Fetch", command=self.fetch_feed
        )
        fetch_btn.pack(side="left", padx=(5, 0))

        # 2) Listbox for titles
        self.listbox = tk.Listbox(self)
        self.listbox.pack(fill="both", expand=True, padx=10, pady=5)
        self.listbox.bind("<Double-1>", self.open_entry)

        # 3) Store parsed entries
        self.entries = []

    def fetch_feed(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("No URL", "Please enter an RSS feed URL.")
            return

        # parse the feed
        feed = feedparser.parse(url)
        if feed.bozo:
            messagebox.showerror(
                "Fetch Error", f"Could not parse feed:\n{feed.bozo_exception}"
            )
            return

        # clear old items
        self.listbox.delete(0, tk.END)
        self.entries = feed.entries

        # populate listbox
        for entry in self.entries:
            self.listbox.insert(tk.END, entry.title)

    def open_entry(self, event):
        sel = self.listbox.curselection()
        if not sel:
            return
        entry = self.entries[sel[0]]
        webbrowser.open(entry.link)


def main():
    app = RSSReader()
    app.mainloop()


if __name__ == "__main__":
    main()
