"""
GUI components for RSS Reader.

This module contains the main application window and user interface logic.
"""

import tkinter as tk
import webbrowser
from tkinter import messagebox, simpledialog, ttk
from typing import Dict, List

from .audio_player import AudioPlayer, check_audio_support
from .feeds import (
    get_entry_audio_url,
    get_entry_duration,
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
        self.geometry("800x500")  # Made wider for audio controls

        # Load title→URL mapping
        self.feeds: Dict[str, str] = load_saved_feeds()
        self.entries: List = []

        # Audio player setup
        self.audio_player = None
        self.audio_supported = check_audio_support()
        if self.audio_supported:
            try:
                self.audio_player = AudioPlayer()
            except ImportError as e:
                self.audio_supported = False
                print(f"Audio not available: {e}")

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

        # Main content frame
        content_frame = ttk.Frame(self)
        content_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Left side: Listbox for feed entries
        left_frame = ttk.Frame(content_frame)
        left_frame.pack(side="left", fill="both", expand=True)

        self.listbox = tk.Listbox(left_frame)
        self.listbox.pack(fill="both", expand=True)
        self.listbox.bind("<Double-1>", self.open_entry)
        self.listbox.bind("<<ListboxSelect>>", self.on_entry_select)

        # Right side: Audio controls (if supported)
        if self.audio_supported:
            self._setup_audio_controls(content_frame)

    def _setup_audio_controls(self, parent) -> None:
        """Set up audio playback controls."""
        audio_frame = ttk.LabelFrame(parent, text="Audio Player", padding=10)
        audio_frame.pack(side="right", fill="y", padx=(10, 0))

        # Current track info
        self.current_track_var = tk.StringVar(value="No track selected")
        track_label = ttk.Label(
            audio_frame,
            textvariable=self.current_track_var,
            wraplength=200,
            font=("TkDefaultFont", 9, "bold"),
        )
        track_label.pack(pady=(0, 10))

        # Playback controls
        controls_frame = ttk.Frame(audio_frame)
        controls_frame.pack(fill="x", pady=5)

        self.play_btn = ttk.Button(
            controls_frame,
            text="▶ Play",
            command=self.play_audio,
            state="disabled",
        )
        self.play_btn.pack(side="left", padx=2)

        self.pause_btn = ttk.Button(
            controls_frame,
            text="⏸ Pause",
            command=self.pause_audio,
            state="disabled",
        )
        self.pause_btn.pack(side="left", padx=2)

        self.stop_btn = ttk.Button(
            controls_frame,
            text="⏹ Stop",
            command=self.stop_audio,
            state="disabled",
        )
        self.stop_btn.pack(side="left", padx=2)

        # Volume control
        volume_frame = ttk.Frame(audio_frame)
        volume_frame.pack(fill="x", pady=10)

        ttk.Label(volume_frame, text="Volume:").pack(anchor="w")
        self.volume_var = tk.DoubleVar(value=0.7)
        volume_scale = ttk.Scale(
            volume_frame,
            from_=0.0,
            to=1.0,
            variable=self.volume_var,
            orient="horizontal",
            command=self.on_volume_change,
        )
        volume_scale.pack(fill="x", pady=2)

        # Status
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(
            audio_frame,
            textvariable=self.status_var,
            font=("TkDefaultFont", 8),
        )
        status_label.pack(pady=(10, 0))

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
            # Add duration info if available
            duration = get_entry_duration(entry)
            if duration:
                title += f" [{duration}]"
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

    def on_entry_select(self, event) -> None:
        """Handle selection of a feed entry."""
        if not self.audio_supported:
            return

        selection = self.listbox.curselection()
        if not selection:
            return

        entry = self.entries[selection[0]]
        title = get_entry_title(entry)
        audio_url = get_entry_audio_url(entry)

        if audio_url:
            self.current_track_var.set(f"Selected: {title[:50]}...")
            self.play_btn.config(state="normal")
            self.status_var.set("Audio available - click Play")
        else:
            self.current_track_var.set("No audio available")
            self.play_btn.config(state="disabled")
            self.pause_btn.config(state="disabled")
            self.stop_btn.config(state="disabled")
            self.status_var.set("No audio track found")

    def play_audio(self) -> None:
        """Start playing the selected audio."""
        if not self.audio_player:
            return

        selection = self.listbox.curselection()
        if not selection:
            return

        entry = self.entries[selection[0]]
        audio_url = get_entry_audio_url(entry)

        if not audio_url:
            messagebox.showwarning(
                "No Audio", "This entry doesn't have audio available."
            )
            return

        self.status_var.set("Loading audio...")
        self.play_btn.config(state="disabled")

        # Load and play in a separate thread to avoid freezing UI
        def load_and_play():
            try:
                if self.audio_player.load_url(audio_url):
                    self.audio_player.set_volume(self.volume_var.get())
                    self.audio_player.play()

                    # Update UI on main thread
                    self.after(0, lambda: self._on_playback_started())
                else:
                    self.after(
                        0,
                        lambda: self._on_playback_error(
                            "Failed to load audio"
                        ),
                    )
            except Exception as error:
                error_msg = str(error)
                self.after(0, lambda: self._on_playback_error(error_msg))

        import threading

        threading.Thread(target=load_and_play, daemon=True).start()

    def _on_playback_started(self) -> None:
        """Called when playback successfully starts."""
        self.status_var.set("Playing...")
        self.play_btn.config(state="disabled")
        self.pause_btn.config(state="normal")
        self.stop_btn.config(state="normal")

    def _on_playback_error(self, error: str) -> None:
        """Called when playback fails."""
        self.status_var.set(f"Error: {error}")
        self.play_btn.config(state="normal")
        self.pause_btn.config(state="disabled")
        self.stop_btn.config(state="disabled")

    def pause_audio(self) -> None:
        """Pause audio playback."""
        if self.audio_player:
            self.audio_player.pause()
            self.status_var.set("Paused")
            self.play_btn.config(state="normal")
            self.pause_btn.config(state="disabled")

    def stop_audio(self) -> None:
        """Stop audio playback."""
        if self.audio_player:
            self.audio_player.stop()
            self.status_var.set("Stopped")
            self.play_btn.config(state="normal")
            self.pause_btn.config(state="disabled")
            self.stop_btn.config(state="disabled")

    def on_volume_change(self, value) -> None:
        """Handle volume slider changes."""
        if self.audio_player:
            self.audio_player.set_volume(float(value))

    def destroy(self) -> None:
        """Clean up resources when closing the app."""
        if self.audio_player:
            self.audio_player.cleanup()
        super().destroy()
