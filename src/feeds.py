"""
Feed management utilities for RSS Reader.

This module handles loading, saving, and parsing RSS feeds.
"""

import json
import os
from typing import Dict

import feedparser

FEEDS_FILE = "feeds.json"
DEFAULT_FEEDS = {
    "Google News": "https://news.google.com/rss",
    "Modern Wisdom": "https://podcasts.apple.com/gb/feed/podcast/modern-wisdom/id1347973549/rss",
}


def load_saved_feeds() -> Dict[str, str]:
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


def save_saved_feeds(feeds_dict: Dict[str, str]) -> None:
    """Save dict of {title: url} to JSON."""
    with open(FEEDS_FILE, "w") as f:
        json.dump(feeds_dict, f, indent=2)


def parse_feed(url: str):
    """Parse an RSS feed from the given URL."""
    return feedparser.parse(url)


def get_entry_link(entry) -> str | None:
    """Extract a link from a feed entry, trying multiple methods."""
    # Try to get link from the links list first, then fallback to id
    link = None
    if hasattr(entry, "links") and entry.links:
        # Get the first link that has an href
        for link_obj in entry.links:
            if hasattr(link_obj, "href"):
                link = link_obj.href
                break

    # Fallback to id if no link found
    if not link:
        link = getattr(entry, "id", None)

    return link


def get_entry_title(entry) -> str:
    """Extract a title from a feed entry safely."""
    title = getattr(entry, "title", "Untitled")
    return str(title)


def get_entry_audio_url(entry) -> str | None:
    """Extract audio URL from a feed entry (for podcasts)."""
    if hasattr(entry, "links") and entry.links:
        # Look for audio links (common audio MIME types)
        audio_types = [
            "audio/mpeg",
            "audio/mp3",
            "audio/x-mp3",
            "audio/mp4",
            "audio/m4a",
            "audio/x-m4a",
            "audio/wav",
            "audio/ogg",
            "audio/webm",
        ]

        for link_obj in entry.links:
            if hasattr(link_obj, "type") and link_obj.type in audio_types:
                return getattr(link_obj, "href", None)

            # Also check for .mp3, .m4a, .wav file extensions
            if hasattr(link_obj, "href"):
                href = link_obj.href.lower()
                if any(
                    href.endswith(ext)
                    for ext in [".mp3", ".m4a", ".wav", ".ogg"]
                ):
                    return link_obj.href

    # Fallback: check enclosures (common in podcast feeds)
    if hasattr(entry, "enclosures") and entry.enclosures:
        for enclosure in entry.enclosures:
            if hasattr(enclosure, "type") and "audio" in enclosure.type:
                return getattr(enclosure, "href", None)

    return None


def get_entry_duration(entry) -> str | None:
    """Extract duration from a feed entry if available."""
    # Check for iTunes duration
    duration = getattr(entry, "itunes_duration", None)
    if duration:
        return str(duration)

    # Check in enclosures
    if hasattr(entry, "enclosures") and entry.enclosures:
        for enclosure in entry.enclosures:
            if hasattr(enclosure, "length"):
                # Convert bytes to approximate duration (rough estimate)
                try:
                    length_bytes = int(enclosure.length)
                    # Rough estimate: 1MB ≈ 1 minute for audio
                    minutes = length_bytes // (1024 * 1024)
                    return f"~{minutes} min"
                except (ValueError, AttributeError):
                    pass

    return None
