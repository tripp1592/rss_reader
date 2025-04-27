# RSS Reader

A Python-based RSS feed reader application that allows you to subscribe to, retrieve, and read RSS feeds. This implementation follows the [RSS 2.0 Specification](https://www.rssboard.org/rss-specification).

## Features

- Subscribe to multiple RSS feeds
- Fetch and parse RSS feed content
- View feed entries in a clean interface
- Save feeds for later reading
- SQLite database storage for feed persistence

## Technical Details

This application implements the RSS 2.0 specification, which includes support for:
- Channel elements (title, link, description, etc.)
- Item elements (title, link, description, author, etc.)
- Proper XML parsing and rendering
- SQLite database for storing feed data

## Installation

This project uses the UV package manager for Python.

### Prerequisites

- Python 3.8+
- UV package manager

### Installing UV

#### Powershell (Windows)
```powershell
curl -sSf https://install.python-uv.org/v0.1.25 | python -
```

#### Bash (Linux/macOS)
```bash
curl -sSf https://install.python-uv.org/v0.1.25 | python3 -
```

#### Zsh (macOS)
```zsh
curl -sSf https://install.python-uv.org/v0.1.25 | python3 -
```

### Setting up the project

1. Clone the repository:

#### Powershell
```powershell
git clone https://github.com/yourusername/rss_reader.git
cd rss_reader
```

#### Bash/Zsh
```bash
git clone https://github.com/yourusername/rss_reader.git
cd rss_reader
```

2. Create a virtual environment:

#### Powershell
```powershell
uv venv
```

#### Bash/Zsh
```bash
uv venv
```

3. Activate the virtual environment:

#### Powershell
```powershell
.\.venv\Scripts\Activate.ps1
```

#### Bash/Zsh
```bash
source .venv/bin/activate
```

4. Install dependencies:

#### All Platforms
```
uv pip install -r requirements.txt
```

## Usage

Run the application:

#### Powershell
```powershell
uv run main.py
```

#### Bash/Zsh
```bash
uv run main.py
```

## Documentation

RSS 2.0 specification documentation is included in the `docs` folder. The implementation follows this standard for maximum compatibility with modern RSS feeds.

## Configuration

The application stores feed configurations in an SQLite database. You can manage feeds through the application interface.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

