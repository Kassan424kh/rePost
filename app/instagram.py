from __future__ import annotations

import importlib
from pathlib import Path


class InstagramUploadError(RuntimeError):
    pass


def upload_reel(
    *,
    file_path: Path,
    caption: str,
    username: str,
    password: str,
    session_path: str,
) -> str:
    if not username or not password:
        raise InstagramUploadError("Missing Instagram username or password")

    instagrapi_module = importlib.import_module("instagrapi")
    client_class = getattr(instagrapi_module, "Client")
    client = client_class()
    session_file = Path(session_path)

    if session_file.exists():
        client.load_settings(str(session_file))

    logged_in = False
    if client.user_id:
        try:
            client.get_timeline_feed()
            logged_in = True
        except Exception:
            logged_in = False

    if not logged_in:
        try:
            client.login(username, password)
        except Exception as exc:
            raise InstagramUploadError(f"Instagram login failed: {exc}") from exc

    try:
        media = client.clip_upload(path=str(file_path), caption=caption)
    except Exception as exc:
        raise InstagramUploadError(f"Instagram reel upload failed: {exc}") from exc

    session_file.write_text(client.dumps_settings())
    media_id = getattr(media, "id", None) or str(getattr(media, "pk", ""))
    return str(media_id)
