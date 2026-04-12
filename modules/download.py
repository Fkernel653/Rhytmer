from yt_dlp import YoutubeDL
from fake_useragent import UserAgent
from modules.add_metadata import add_metadata
from dataclasses import dataclass
from typing import Optional, Callable
from pathlib import Path

@dataclass
class Download:
    """Handles audio download from URL using yt-dlp"""
    url: str
    codec: Optional[str]
    kbps: Optional[int]
    progress_callback: Optional[Callable] = None

    path = Path.home()  # Download to user's home directory
    ua = UserAgent().random  # Random user-agent to avoid blocking

    def set_progress_callback(self, callback):
        """Register callback for progress updates"""
        self.progress_callback = callback

    def progress_hook(self, d):
        """yt-dlp progress hook - extracts percentage and calls callback"""
        if d["status"] == "downloading":
            percent = d.get("_percent_str", "0%").rstrip("%")
            try:
                percent = float(percent)
            except ValueError:
                percent = 0
            # Fallback calculation if percent string is unreliable
            if "total_bytes" in d and d["total_bytes"] > 0:
                percent = (d["downloaded_bytes"] / d["total_bytes"]) * 100
            elif "total_bytes_estimate" in d and d["total_bytes_estimate"] > 0:
                percent = (d["downloaded_bytes"] / d["total_bytes_estimate"]) * 100

            if self.progress_callback and percent > 0:
                try:
                    self.progress_callback(int(percent))
                except Exception:
                    pass
        elif d["status"] == "processing":
            if self.progress_callback:
                self.progress_callback(99)  # Almost done
        elif d["status"] == "finished":
            if self.progress_callback:
                self.progress_callback(100)  # Complete

    def normal(self) -> bool:
        """
        Download audio using yt-dlp with post-processing:
        - Extract audio to specified codec/bitrate
        - Embed thumbnail
        - Return True if metadata added successfully
        """
        opts = {
            "user_agent": self.ua,
            "format": "bestaudio/best",
            "outtmpl": str(self.path / "%(title)s.%(ext)s"),
            "writethumbnail": True,  # download thumbnail for embedding
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": self.codec,
                    "preferredquality": self.kbps,
                },
                {
                    "key": "EmbedThumbnail",  # embed thumbnail into audio file
                },
            ],
            "progress_hooks": [self.progress_hook],
            "quiet": True,
            "no_warnings": True,
            "ignoreerrors": False,
            "nooverwrites": True,
        }

        with YoutubeDL(opts) as ydl:
            # Extract video info without downloading
            info = ydl.extract_info(self.url, download=False)

            # Perform actual download with post-processing
            ydl.process_info(info)

            filename = ydl.prepare_filename(info)  # get expected output path

        file_path = Path(filename)

        # Extract metadata from video info
        title = info.get("title", "Unknown Title")
        artist = info.get("uploader", info.get("channel", "Unknown Artist"))
        album = info.get("album", info.get("channel"))

        # Add metadata tags to downloaded file
        return add_metadata(
            file=file_path, codec=self.codec, title=title, artist=artist, album=album
        )