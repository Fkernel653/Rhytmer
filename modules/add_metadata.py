from mutagen.id3 import ID3, TIT2, TPE1, TALB
from pathlib import Path


def add_metadata(file: Path, codec: str, title: str, artist: str, album: str):
    """
    Add metadata tags (title, artist, album) to audio file.
    Returns True if successful, False otherwise.
    """
    if not file.exists():
        return False

    try:
        match codec.lower():
            case "m4a":
                from mutagen.mp4 import MP4

                audio = MP4(file)
                if title:
                    audio["\xa9nam"] = title
                if artist:
                    audio["\xa9ART"] = artist
                if album:
                    audio["\xa9alb"] = album
                audio.save()
                return True

            case "flac":
                from mutagen.flac import FLAC

                audio = FLAC(file)
                if title:
                    audio["title"] = title
                if artist:
                    audio["artist"] = artist
                if album:
                    audio["album"] = album
                audio.save()
                return True

            case "opus":
                from mutagen.oggopus import OggOpus

                audio = OggOpus(file)
                if title:
                    audio["title"] = title
                if artist:
                    audio["artist"] = artist
                if album:
                    audio["album"] = album
                audio.save()
                return True

            case "mp3":
                from mutagen.mp3 import MP3

                audio = MP3(file, ID3=ID3)
                if audio.tags is None:
                    audio.add_tags()
                if title:
                    audio.tags.add(TIT2(encoding=3, text=title))
                if artist:
                    audio.tags.add(TPE1(encoding=3, text=artist))
                if album:
                    audio.tags.add(TALB(encoding=3, text=album))
                audio.save()
                return True

            case _:
                return False
    except Exception:
        # Log error but don't fail the whole download
        return False
