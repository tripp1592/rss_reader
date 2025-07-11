"""
Audio player functionality for RSS Reader.

This module handles audio playback for podcast episodes.
"""

import os
import tempfile
from typing import Callable, Optional

import requests

try:
    import pygame

    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False


class AudioPlayer:
    """Simple audio player using pygame for podcast playback."""

    def __init__(self):
        self.is_playing = False
        self.is_paused = False
        self.current_file = None
        self.position_callback: Optional[Callable] = None

        if PYGAME_AVAILABLE:
            pygame.mixer.init()
        else:
            raise ImportError(
                "pygame is required for audio playback. Install with: uv pip install pygame"
            )

    def load_url(self, url: str) -> bool:
        """Load audio from URL (downloads to temp file)."""
        try:
            # Download audio file to temporary location
            response = requests.get(url, stream=True)
            response.raise_for_status()

            # Create temp file with appropriate extension
            suffix = ".mp3"  # Default to mp3
            if url.lower().endswith(".m4a"):
                suffix = ".m4a"
            elif url.lower().endswith(".wav"):
                suffix = ".wav"
            elif url.lower().endswith(".ogg"):
                suffix = ".ogg"

            temp_file = tempfile.NamedTemporaryFile(
                delete=False, suffix=suffix
            )

            # Download in chunks
            for chunk in response.iter_content(chunk_size=8192):
                temp_file.write(chunk)

            temp_file.close()
            self.current_file = temp_file.name

            # Load into pygame
            pygame.mixer.music.load(self.current_file)
            return True

        except Exception as e:
            print(f"Error loading audio from URL: {e}")
            return False

    def play(self) -> None:
        """Start or resume playback."""
        if not self.current_file:
            return

        if self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False
        else:
            pygame.mixer.music.play()

        self.is_playing = True

    def pause(self) -> None:
        """Pause playback."""
        if self.is_playing:
            pygame.mixer.music.pause()
            self.is_paused = True
            self.is_playing = False

    def stop(self) -> None:
        """Stop playback."""
        pygame.mixer.music.stop()
        self.is_playing = False
        self.is_paused = False

        # Clean up temp file
        if self.current_file and os.path.exists(self.current_file):
            try:
                os.unlink(self.current_file)
            except OSError:
                pass  # File might be in use
        self.current_file = None

    def set_volume(self, volume: float) -> None:
        """Set volume (0.0 to 1.0)."""
        pygame.mixer.music.set_volume(max(0.0, min(1.0, volume)))

    def get_playing(self) -> bool:
        """Check if currently playing."""
        return self.is_playing and pygame.mixer.music.get_busy()

    def cleanup(self) -> None:
        """Clean up resources."""
        self.stop()
        if PYGAME_AVAILABLE:
            pygame.mixer.quit()


def check_audio_support() -> bool:
    """Check if audio playback is supported."""
    return PYGAME_AVAILABLE
