from __future__ import annotations

import importlib
import re
from pathlib import Path


class InstagramUploadError(RuntimeError):
    pass


def _normalize_session_id(raw_value: str) -> str:
    value = (raw_value or "").strip().strip('"').strip("'")
    if not value:
        return ""

    match = re.search(r"sessionid=([^;\s]+)", value)
    if match:
        return match.group(1).strip()

    return value


def upload_reel(
    *,
    file_path: Path,
    caption: str,
    username: str,
    password: str,
    session_id: str,
    session_path: str,
) -> str:
    normalized_session_id = _normalize_session_id(session_id)
    if not session_id and (not username or not password):
        raise InstagramUploadError(
            "Missing Instagram credentials: provide INSTAGRAM_SESSION_ID or username/password"
        )

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

    session_login_error: Exception | None = None
    if not logged_in and normalized_session_id:
        try:
            client.login_by_sessionid(normalized_session_id)
            logged_in = True
        except Exception as exc:
            session_login_error = exc

    if not logged_in:
        if not username or not password:
            if session_login_error:
                raise InstagramUploadError(
                    "Instagram session login failed. Ensure INSTAGRAM_SESSION_ID contains only the session value (or cookie string with sessionid=...). "
                    f"Original error: {session_login_error}"
                ) from session_login_error
            raise InstagramUploadError("Missing Instagram username or password")

        try:
            client.login(username, password)
        except Exception as exc:
            error_text = str(exc)
            if session_login_error:
                raise InstagramUploadError(
                    "Instagram session login failed and password login failed. "
                    f"Session error: {session_login_error}; Password error: {exc}"
                ) from exc
            if "572" in error_text or "accounts/login" in error_text:
                raise InstagramUploadError(
                    "Instagram login blocked (HTTP 572). Use INSTAGRAM_SESSION_ID from a valid logged-in session or run from a trusted residential IP."
                ) from exc
            raise InstagramUploadError(f"Instagram login failed: {exc}") from exc

    try:
        media = client.clip_upload(path=str(file_path), caption=caption)
    except Exception as exc:
        error_text = str(exc)
        if "challenge_required" in error_text.lower():
            raise InstagramUploadError(
                "Instagram challenge required. Complete verification once in the Instagram mobile app/web for this account, then refresh INSTAGRAM_SESSION_ID and retry from the same trusted IP/device."
            ) from exc
        raise InstagramUploadError(f"Instagram reel upload failed: {exc}") from exc

    session_file.parent.mkdir(parents=True, exist_ok=True)
    session_file.write_text(client.dumps_settings())
    media_id = getattr(media, "id", None) or str(getattr(media, "pk", ""))
    return str(media_id)
