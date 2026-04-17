from yt_dlp import YoutubeDL
from modules.add_metadata import add_metadata
from dataclasses import dataclass, field
from typing import Optional, Callable
from pathlib import Path
import json
import threading


@dataclass
class DownloadConfig:
    """Configuration constants for Download class"""

    @staticmethod
    def get_config_path() -> Path:
        """Get config file path relative to project root"""
        return Path(__file__).parent.parent / "config.json"


class DownloadError(Exception):
    """Custom exception for download errors"""

    pass


class DownloadCancelledError(DownloadError):
    """Exception raised when download is cancelled by user"""

    pass


@dataclass
class Download:
    """Handles audio download from URL using yt-dlp"""

    url: str
    codec: Optional[str]
    kbps: Optional[int]
    # Callbacks for progress and cancellation
    progress_callback: Optional[Callable] = field(default=None, repr=False)
    cancel_check_callback: Optional[Callable] = field(default=None, repr=False)

    # Instance fields (not in constructor)
    _config_path: Path = field(
        default_factory=DownloadConfig.get_config_path, init=False, repr=False
    )
    _ydl: Optional[YoutubeDL] = field(default=None, init=False, repr=False)
    _cancelled: bool = field(default=False, init=False, repr=False)
    _lock: threading.Lock = field(
        default_factory=threading.Lock, init=False, repr=False
    )

    def _validate_config_file(self) -> None:
        """Check if config file exists, raise exception if not found."""
        if not self._config_path.exists():
            raise DownloadError(
                f"Config file not found at {self._config_path}\n"
                "Please run 'config' command first to set download path."
            )

    def _get_download_path(self) -> Path:
        """Read and validate download path from config file."""
        self._validate_config_file()

        try:
            with open(self._config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                path_str = data.get("path")

                if not path_str:
                    raise DownloadError("Config file missing 'path' key")

                path = Path(path_str)
                # Create directory if it doesn't exist
                if not path.exists():
                    path.mkdir(parents=True, exist_ok=True)

                return path

        except json.JSONDecodeError as e:
            raise DownloadError(f"Config file is corrupted: {e}")

    def set_progress_callback(self, callback: Callable) -> None:
        """Register callback for progress updates"""
        self.progress_callback = callback

    def set_cancel_check(self, callback: Callable) -> None:
        """Register callback to check if download should be cancelled"""
        self.cancel_check_callback = callback

    def cancel(self) -> None:
        """Cancel the current download"""
        with self._lock:
            self._cancelled = True
            if self._ydl:
                try:
                    # Attempt to interrupt yt-dlp
                    self._ydl.params["quiet"] = True
                except Exception:
                    pass

    def _check_cancelled(self) -> None:
        """Check if download was cancelled and raise exception if so"""
        if self._cancelled:
            raise DownloadCancelledError("Download cancelled by user")

        # Also check external callback
        if self.cancel_check_callback and self.cancel_check_callback():
            with self._lock:
                self._cancelled = True
            raise DownloadCancelledError("Download cancelled by user")

    def progress_hook(self, d: dict) -> None:
        """yt-dlp progress hook - extracts percentage and calls callback"""
        # Check for cancellation
        try:
            self._check_cancelled()
        except DownloadCancelledError:
            # Signal yt-dlp to stop by raising an exception
            raise Exception("Download cancelled")

        if not self.progress_callback:
            return

        if d["status"] == "downloading":
            percent = 0

            # Try to get percentage string from yt-dlp
            percent_str = d.get("_percent_str", "0%").rstrip("%")
            try:
                percent = float(percent_str)
            except ValueError:
                pass

            # Fallback calculation if percent string is unreliable
            if percent == 0:
                if "total_bytes" in d and d["total_bytes"] and d["total_bytes"] > 0:
                    percent = (d.get("downloaded_bytes", 0) / d["total_bytes"]) * 100
                elif (
                    "total_bytes_estimate" in d
                    and d["total_bytes_estimate"]
                    and d["total_bytes_estimate"] > 0
                ):
                    percent = (
                        d.get("downloaded_bytes", 0) / d["total_bytes_estimate"]
                    ) * 100

            # Report progress (cap at 99% until processing finishes)
            if percent > 0:
                try:
                    self.progress_callback(int(min(percent, 99)))
                except Exception:
                    pass

        elif d["status"] == "processing":
            # Post-processing phase
            try:
                self.progress_callback(99)
            except Exception:
                pass

        elif d["status"] == "finished":
            # Download complete
            try:
                self.progress_callback(100)
            except Exception:
                pass

    def download(self) -> bool:
        """
        Download audio using yt-dlp with post-processing.

        Returns:
            bool: True if download and metadata addition successful

        Raises:
            DownloadError: If config is invalid or download fails
            DownloadCancelledError: If download is cancelled by user
        """
        # Check if already cancelled
        self._check_cancelled()

        download_path = self._get_download_path()

        # Configure yt-dlp options
        opts = {
            "format": "bestaudio/best",
            "outtmpl": str(download_path / "%(title)s.%(ext)s"),
            "writethumbnail": True,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": self.codec,
                    "preferredquality": str(self.kbps),
                },
                {
                    "key": "EmbedThumbnail",  # Embed thumbnail as cover art
                },
            ],
            "progress_hooks": [self.progress_hook],
            "quiet": True,
            "no_warnings": True,
            "ignoreerrors": False,
            "nooverwrites": True,  # Skip existing files
        }

        try:
            with YoutubeDL(opts) as ydl:
                with self._lock:
                    self._ydl = ydl

                # Check cancellation before starting
                self._check_cancelled()

                # Extract video info without downloading first
                info = ydl.extract_info(self.url, download=False)

                # Get expected output path
                filename = ydl.prepare_filename(info)

                # Handle playlist templates (they contain '%' placeholders)
                if "%" in filename:
                    # For playlists, we need to get the actual file path after download
                    file_path = None
                else:
                    file_path = Path(filename).with_suffix(f".{self.codec}")

                # Perform actual download with post-processing
                ydl.process_info(info)

                # If we couldn't determine the path before, get it from the downloaded info
                if file_path is None:
                    if "requested_downloads" in info and info["requested_downloads"]:
                        filename = info["requested_downloads"][0].get("filepath", "")
                        if filename:
                            file_path = Path(filename)
                        else:
                            raise DownloadError(
                                "Could not determine downloaded file path"
                            )
                    else:
                        raise DownloadError("Could not determine downloaded file path")

                # Extract metadata for tagging
                title = info.get("title", "")
                channel = info.get("channel", "")
                artist = info.get("uploader") or channel or ""
                album = info.get("album") or channel or ""

                # Check cancellation before adding metadata
                self._check_cancelled()

            # Add metadata tags to downloaded file
            result = add_metadata(
                file=file_path,
                codec=self.codec,
                title=title,
                artist=artist,
                album=album,
            )

            # Final progress update
            if self.progress_callback:
                try:
                    self.progress_callback(100)
                except Exception:
                    pass

            return result

        except DownloadCancelledError:
            # Re-raise cancellation exception
            raise
        except Exception as e:
            # Check if this was caused by cancellation
            if self._cancelled or (
                self.cancel_check_callback and self.cancel_check_callback()
            ):
                raise DownloadCancelledError("Download cancelled by user")

            # Handle specific yt-dlp errors with user-friendly messages
            error_msg = str(e)
            if "HTTP Error 403" in error_msg:
                raise DownloadError(
                    "Access forbidden (403). The site may be blocking the request."
                )
            elif "HTTP Error 404" in error_msg:
                raise DownloadError("Video not found (404). Please check the URL.")
            elif "Unsupported URL" in error_msg:
                raise DownloadError(f"Unsupported URL: {self.url}")
            elif "This video is not available" in error_msg:
                raise DownloadError("This video is not available or is private.")
            elif "Sign in to confirm your age" in error_msg:
                raise DownloadError("This video requires age verification.")
            else:
                raise DownloadError(f"Download failed: {e}")
        finally:
            # Clean up yt-dlp reference
            with self._lock:
                self._ydl = None
