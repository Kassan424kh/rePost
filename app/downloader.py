from pathlib import Path
from typing import Tuple
import os

from yt_dlp import YoutubeDL


def _download_with_options(url: str, download_dir: Path, ydl_opts: dict) -> Tuple[Path, dict]:
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        file_path = Path(ydl.prepare_filename(info))

    if not file_path.exists() or file_path.stat().st_size == 0:
        raise RuntimeError("Downloaded file is empty.")

    return file_path, info


def download_short(url: str, download_dir: str) -> Tuple[Path, dict]:
    download_path = Path(download_dir)
    download_path.mkdir(parents=True, exist_ok=True)

    cookies_path = os.environ.get("YTDLP_COOKIES_PATH")

    base_opts = {
        "outtmpl": str(download_path / "%(id)s.%(ext)s"),
        "noplaylist": True,
        "quiet": True,
        "retries": 3,
        "fragment_retries": 3,
        "concurrent_fragment_downloads": 4,
        "http_headers": {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        },
        "extractor_args": {"youtube": {"player_client": ["web"]}},
        "merge_output_format": "mp4",
        "geo_bypass": True,
    }

    if cookies_path:
        base_opts["cookiefile"] = cookies_path

    try:
        return _download_with_options(
            url,
            download_path,
            {**base_opts, "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best"},
        )
    except Exception:
        return _download_with_options(
            url,
            download_path,
            {**base_opts, "format": "bestvideo*+bestaudio*/best"},
        )
