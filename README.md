# RSS Reader

A modern RSS feed reader application built with Python and tkinter, featuring audio playback for podcast episodes.

## Features

🎵 **Audio Playback**
- Stream podcast episodes directly in the app
- Play/Pause/Stop controls with volume adjustment
- Supports MP3, M4A, WAV, and OGG audio formats
- Background audio streaming with progress tracking

📡 **RSS Feed Management**
- Subscribe to multiple RSS feeds
- Save and organize favorite feeds
- Support for premium podcast feeds with authentication
- Automatic feed parsing and episode detection

🎧 **Podcast-Focused Interface**
- Clean, intuitive user interface
- Episode duration display when available
- Visual indicators for audio-enabled episodes
- Easy episode navigation and selection

## Installation

### Prerequisites
- Python 3.9 or later
- uv package manager

### Setup

```bash
# Clone the repository
git clone https://github.com/tripp1592/rss_reader.git
cd rss_reader

# Create virtual environment with uv
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv sync
```

### Required Dependencies

The application requires the following packages:
- `feedparser` - RSS feed parsing
- `pygame` - Audio playback functionality
- `requests` - HTTP requests for feed fetching
- `tkinter` - GUI framework (usually included with Python)

## Usage

### Running the Application

```bash
# Run the main application
uv run main.py
```

### Basic Usage

1. **Add RSS Feeds**
   - Click "Save" to add a new feed
   - Enter the RSS URL and give it a name
   - Select from saved feeds using the dropdown

2. **Browse Episodes**
   - Select a feed and click "Fetch" to load episodes
   - Episodes are displayed in the left panel
   - Audio-enabled episodes show duration when available

3. **Play Audio**
   - Click on an episode to select it
   - Use the audio controls on the right panel
   - Adjust volume with the slider
   - Play/Pause/Stop controls available

### Premium Podcast Support

The app supports premium podcast feeds with authentication:

```
# Examples of supported premium RSS formats
https://feeds.example.com/premium?token=your_token
https://api.example.com/rss?key=your_api_key
```

## Configuration

### Default Feeds

The application comes with a default podcast feed (Modern Wisdom). You can:
- Add more feeds using the "Save" button
- Remove feeds by editing the `feeds.json` file
- Organize feeds by category (manual editing)

### Settings File

Configuration is stored in `feeds.json`:
```json
[
  "https://feeds.simplecast.com/tOjNXDuO",
  "https://your-premium-feed.com/rss?token=abc123"
]
```

## Architecture

The application follows a clean, modular architecture:

```
rss_reader/
├── main.py                 # Entry point
├── src/
│   ├── __init__.py        # Package initialization
│   ├── gui.py             # GUI components and main application
│   ├── feeds.py           # RSS feed management and parsing
│   └── audio_player.py    # Audio playback functionality
├── feeds.json             # Saved RSS feeds
├── pyproject.toml         # Project dependencies
└── README.md              # This file
```

### Module Responsibilities

- **`main.py`** - Simple entry point that launches the GUI
- **`src/gui.py`** - Main GUI class with tkinter interface and event handling
- **`src/feeds.py`** - RSS feed operations (parsing, saving, loading)
- **`src/audio_player.py`** - Audio playback using pygame mixer

## Development

### Running Tests

```bash
# Run type checking
uv run -m mypy src/

# Run code formatting
uv run -m black src/

# Run linting
uv run -m flake8 src/
```

### Project Structure

The project follows Python best practices:
- **Type hints** throughout the codebase
- **Error handling** for network and audio operations
- **Modular design** with separation of concerns
- **Documentation** with docstrings for all functions

### Adding New Features

To extend the application:

1. **New audio formats** - Add support in `audio_player.py`
2. **UI improvements** - Modify the GUI in `gui.py`
3. **Feed processing** - Extend functionality in `feeds.py`
4. **Configuration** - Add settings management

## Dependencies

### Core Dependencies
```toml
[project]
dependencies = [
    "feedparser>=6.0.0",
    "pygame>=2.0.0",
    "requests>=2.28.0",
]
```

### Development Dependencies
```toml
[project.optional-dependencies]
dev = [
    "black>=22.0.0",
    "flake8>=5.0.0",
    "mypy>=1.0.0",
    "pytest>=7.0.0",
]
```

## Troubleshooting

### Common Issues

**Audio not playing:**
- Ensure pygame is installed: `uv add pygame`
- Check if the podcast provides audio URLs
- Verify network connection for streaming

**Feed not loading:**
- Verify RSS URL is correct and accessible
- Check if the feed requires authentication
- Ensure network connectivity

**UI not responding:**
- Large audio files may take time to download
- Check system resources and available memory

### System Requirements

- **Operating System**: Windows, macOS, or Linux
- **Memory**: 512MB RAM minimum
- **Storage**: 100MB for application + temp audio files
- **Network**: Internet connection for RSS feeds and audio streaming

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style

- Follow PEP 8 guidelines
- Use type hints for all functions
- Add docstrings for public methods
- Test your changes thoroughly

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with Python and tkinter
- RSS parsing powered by feedparser
- Audio playback using pygame
- Modern Wisdom podcast for default feed example

---

**Note**: This application is designed for personal use and podcast listening. Ensure you have proper permissions for any premium feeds you subscribe to.