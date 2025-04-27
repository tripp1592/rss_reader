# RSS Reader

A Python-based RSS feed reader application that allows you to subscribe to, retrieve, and read RSS feeds.

## Features

- Subscribe to multiple RSS feeds
- Fetch and parse RSS feed content
- View feed entries in a clean interface
- Save feeds for later reading

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

## Configuration

The application stores feed configurations in a JSON file. You can edit this manually or through the application interface.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

