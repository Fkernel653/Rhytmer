# poetry - TUI Audio Downloader

A terminal-based user interface (TUI) for downloading high-quality audio. Built with Python, `yt-dlp`, and `textual` for a modern terminal experience with automatic metadata embedding.

![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-linux%20%7C%20macOS%20%7C%20windows-lightgrey)
![TUI](https://img.shields.io/badge/TUI-textual-purple.svg)

## 📋 Features

### User Interface
- **Modern Terminal UI** – Built with Textual framework
- **Interactive Selectors** – Choose codec and bitrate from dropdown menus
- **Real-time Progress Bar** – Visual feedback during downloads
- **Cancel Support** – Interrupt downloads at any time
- **Theme Support** – Tokyo Night theme by default

### Download Features
- **High-Quality Audio Extraction** – Downloads best available audio stream
- **Multiple Audio Formats** – M4A, AAC, MP3, FLAC, Opus
- **Configurable Bitrate** – 64, 128, 256, or 320 kbps
- **Automatic Metadata Embedding** – Adds title, artist, and album tags
- **Thumbnail Embedding** – Album art automatically embedded into audio files
- **Single URL Mode** – Paste and download one track at a time

## 🚀 Installation

### Prerequisites

- **Python 3.10 or higher** (uses `match` statement)
- **FFmpeg** – Required for audio conversion and thumbnail embedding

### Install FFmpeg

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
1. Download from [FFmpeg.org](https://ffmpeg.org/download.html)
2. Add the `bin` folder to your system PATH
3. Verify: `ffmpeg -version`

### Install poetry

```bash
# Clone the repository
git clone https://github.com/Fkernel653/poetry.git
cd poetry

# Install dependencies
pip install -r requirements.txt
```

## 🎮 Usage

### Launch the TUI

```bash
python main.py
```

### Interface Walkthrough

1. **Enter URL** – Paste a your URL
2. **Select Codec** – Choose audio format (M4A, MP3, AAC, FLAC, Opus)
3. **Select Bitrate** – Choose quality (64–320 kbps)
4. **Click Download** – Start the download with progress bar
5. **Cancel if needed** – Stop an ongoing download

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Tab` | Navigate between widgets |
| `Enter` | Select button or dropdown item |
| `Ctrl+C` | Exit application |

## 📁 Project Structure

```
poetry/
├── main.py                # TUI application entry point
├── requirements.txt       # Python dependencies
├── README.md              # Documentation
├── LICENSE                # MIT License
└── modules/
    ├── __init__.py        # Package initializer
    ├── download.py        # Audio download with yt-dlp & metadata
    └── add_metadata.py    # Metadata tagging for all formats
```

## 🛠️ Technical Details

### Download Pipeline

```
1. Paste URL in TUI
2. Select codec & bitrate
3. Press Download
4. Extract video info (yt-dlp)
5. Download best audio stream
6. Download thumbnail
7. Convert audio (FFmpeg)
8. Embed thumbnail
9. Add metadata tags (mutagen)
10. Save to ~/Music/
11. Show success notification
```

### Supported Formats & Metadata

| Format | Extension | Metadata Library | Tags Added |
|--------|-----------|------------------|-------------|
| M4A/AAC | .m4a/.aac | mutagen.mp4 | `©nam`, `©ART`, `©alb` |
| MP3 | .mp3 | mutagen.id3 | TIT2, TPE1, TALB |
| FLAC | .flac | mutagen.flac | title, artist, album |
| Opus | .opus | mutagen.oggopus | title, artist, album |

### Default Download Location

Audio files are saved to your home directory:
- **Linux/macOS**: `$HOME`
- **Windows**: `C:\Users\<USERNAME>`\ or `C:\Users\<USERNAME>\`

*Note: Currently hardcoded to `Path.home()`. Future versions will support configurable paths.*

## 🎨 TUI Interface Preview

```
┌─────────────────────────────────────────────────────────────┐
│ Poetry                                                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Enter your URL                                     │    │
│  │  https://youtu.be/...                               │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
│  ████████████████████████████████████████ 45%               │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐                         │
│  │ M4A          │  │ 256          │                         │
│  └──────────────┘  └──────────────┘                         │
│                                                             │
│  ┌──────────┐  ┌────────┐                                   │
│  │ Download │  │ Cancel │                                   │
│  └──────────┘  └────────┘                                   │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  Press Ctrl+C to exit                                       │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 Configuration

Currently, poetry downloads to your home directory. To change this, modify the `path` variable in `modules/download.py`:

```python
# In download.py, line ~15
path = Path.home()  # Change to your preferred path
```

Future versions will include a configuration UI.

## 📝 Requirements

### Python Dependencies (`requirements.txt`)

| Package | Purpose |
|---------|---------|
| `yt-dlp` | YouTube downloading and audio extraction |
| `textual` | Terminal UI framework |
| `mutagen` | Audio metadata tagging |
| `fake-useragent` | Random user agent rotation |

### System Dependencies

- **FFmpeg** – Required for audio conversion (must be in PATH)
- **Python 3.10+** – Runtime environment

## 🔥 Usage Examples

### Example 1: Download a single track

```bash
python main.py
# Paste: https://youtu.be/BB_d2-WVgXI
# Select: M4A, 256 kbps
# Click Download
# Output: ✓ Download completed!
```

### Example 2: High-quality MP3

```bash
# Launch app
python main.py
# Select: MP3, 320 kbps
# Paste any URL
# Click Download
```

### Example 3: Lossless FLAC

```bash
# Launch app
python main.py
# Select: FLAC, 256 kbps (bitrate ignored for FLAC)
# Paste URL
# Click Download
```

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| **FFmpeg not found** | Install FFmpeg and ensure it's in PATH |
| **Download stuck at 0%** | Check internet connection and URL validity |
| **Metadata not added** | Check file permissions and format support |
| **TUI doesn't launch** | Run `pip install --upgrade textual` |
| **"No module named modules"** | Run from project root directory |
| **Progress bar not showing** | Resize terminal window or restart app |

### Debug Mode

Add print statements in `download.py` to see yt-dlp output:
```python
# Change in download.py, line ~65
"quiet": False,  # Enable verbose output
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Commit: `git commit -m 'Add amazing feature'`
5. Push: `git push origin feature/amazing-feature`
6. Open a Pull Request

### Code Style
- Follow PEP 8
- Use type hints
- Add docstrings
- Test with different codecs and URLs

## 📄 License

Distributed under the MIT License. See `LICENSE` file for details.

## 👨‍💻 Author

**Fkernel653** – [GitHub](https://github.com/Fkernel653)

## 🙏 Acknowledgments

- [Textual](https://github.com/Textualize/textual) – TUI framework
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) – YouTube download library
- [mutagen](https://github.com/quodlibet/mutagen) – Audio metadata handling
- [fake-useragent](https://github.com/hellysmile/fake-useragent) – User agent rotation

## ⚠️ Disclaimer

**For educational purposes only.** Users are responsible for complying with platform Terms of Service and applicable copyright laws. Download only content you have permission to download.