from __future__ import annotations

import math
import time
from pathlib import Path
from typing import Any

import requests

INIT_URL = "https://open.tiktokapis.com/v2/post/publish/video/init/"
STATUS_URL = "https://open.tiktokapis.com/v2/post/publish/status/fetch/"


class TikTokUploadError(RuntimeError):
    pass


def _auth_headers(access_token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }


def _ensure_ok(response: requests.Response, context: str) -> dict[str, Any]:
    try:
        payload = response.json()
    except Exception as exc:
        raise TikTokUploadError(f"{context}: invalid JSON response") from exc

    if response.status_code >= 400:
        message = payload.get("error", {}).get("message") or payload
        raise TikTokUploadError(f"{context}: {message}")

    error = payload.get("error") or {}
    if error.get("code") not in (None, "ok"):
        raise TikTokUploadError(f"{context}: {error.get('message') or error}")

    return payload


def _upload_file_to_url(upload_url: str, file_path: Path, chunk_size: int) -> None:
    file_size = file_path.stat().st_size
    total_chunks = max(1, math.ceil(file_size / chunk_size))

    with file_path.open("rb") as source:
        for index in range(total_chunks):
            start = index * chunk_size
            end = min(file_size, start + chunk_size) - 1
            current_chunk_size = end - start + 1
            chunk = source.read(current_chunk_size)
            if not chunk:
                raise TikTokUploadError("No video bytes read for TikTok upload chunk")

            headers = {
                "Content-Type": "video/mp4",
                "Content-Length": str(len(chunk)),
                "Content-Range": f"bytes {start}-{end}/{file_size}",
            }
            response = requests.put(upload_url, headers=headers, data=chunk, timeout=120)
            if response.status_code >= 400:
                raise TikTokUploadError(
                    f"TikTok chunk upload failed with status {response.status_code}: {response.text}"
                )


def upload_video(
    *,
    file_path: Path,
    title: str,
    access_token: str,
    privacy_level: str,
    disable_comment: bool,
    disable_duet: bool,
    disable_stitch: bool,
    chunk_size: int = 5 * 1024 * 1024,
    timeout_seconds: int = 120,
) -> str:
    file_size = file_path.stat().st_size
    total_chunk_count = max(1, math.ceil(file_size / chunk_size))

    payload = {
        "post_info": {
            "title": title[:2200],
            "privacy_level": privacy_level,
            "disable_comment": disable_comment,
            "disable_duet": disable_duet,
            "disable_stitch": disable_stitch,
        },
        "source_info": {
            "source": "FILE_UPLOAD",
            "video_size": file_size,
            "chunk_size": chunk_size,
            "total_chunk_count": total_chunk_count,
        },
    }

    init_response = requests.post(
        INIT_URL,
        headers=_auth_headers(access_token),
        json=payload,
        timeout=30,
    )
    init_payload = _ensure_ok(init_response, "TikTok init failed")
    data = init_payload.get("data") or {}

    publish_id = data.get("publish_id")
    upload_url = data.get("upload_url")
    if not publish_id or not upload_url:
        raise TikTokUploadError("TikTok init response missing publish_id or upload_url")

    _upload_file_to_url(upload_url, file_path, chunk_size)

    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        status_response = requests.post(
            STATUS_URL,
            headers=_auth_headers(access_token),
            json={"publish_id": publish_id},
            timeout=30,
        )
        status_payload = _ensure_ok(status_response, "TikTok status check failed")
        status_data = status_payload.get("data") or {}
        status = (status_data.get("status") or "").upper()

        if status in {"PUBLISHED", "SUCCESS"}:
            return publish_id
        if status in {"FAILED", "ERROR", "CANCELED", "CANCELLED"}:
            fail_reason = status_data.get("fail_reason") or status
            raise TikTokUploadError(f"TikTok publish failed: {fail_reason}")

        time.sleep(3)

    return publish_id
