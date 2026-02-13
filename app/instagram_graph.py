from __future__ import annotations

import time
from typing import Any

import requests

GRAPH_BASE_URL = "https://graph.facebook.com/v22.0"


class InstagramGraphUploadError(RuntimeError):
    pass


def _ensure_ok(response: requests.Response, context: str) -> dict[str, Any]:
    try:
        payload = response.json()
    except Exception as exc:
        raise InstagramGraphUploadError(f"{context}: invalid JSON response") from exc

    if response.status_code >= 400:
        error = payload.get("error") or {}
        message = error.get("message") or payload
        raise InstagramGraphUploadError(f"{context}: {message}")

    if payload.get("error"):
        raise InstagramGraphUploadError(f"{context}: {payload['error']}")

    return payload


def upload_reel_from_url(
    *,
    ig_user_id: str,
    access_token: str,
    video_url: str,
    caption: str,
    timeout_seconds: int = 180,
) -> str:
    create_url = f"{GRAPH_BASE_URL}/{ig_user_id}/media"
    create_response = requests.post(
        create_url,
        data={
            "media_type": "REELS",
            "video_url": video_url,
            "caption": caption,
            "access_token": access_token,
        },
        timeout=30,
    )
    create_payload = _ensure_ok(create_response, "Instagram Graph media create failed")
    creation_id = create_payload.get("id")
    if not creation_id:
        raise InstagramGraphUploadError("Instagram Graph media create did not return id")

    status_url = f"{GRAPH_BASE_URL}/{creation_id}"
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        status_response = requests.get(
            status_url,
            params={
                "fields": "status_code",
                "access_token": access_token,
            },
            timeout=30,
        )
        status_payload = _ensure_ok(status_response, "Instagram Graph status check failed")
        status_code = (status_payload.get("status_code") or "").upper()

        if status_code == "FINISHED":
            break
        if status_code == "ERROR":
            raise InstagramGraphUploadError("Instagram Graph media processing failed")

        time.sleep(3)
    else:
        raise InstagramGraphUploadError("Instagram Graph media processing timed out")

    publish_url = f"{GRAPH_BASE_URL}/{ig_user_id}/media_publish"
    publish_response = requests.post(
        publish_url,
        data={
            "creation_id": creation_id,
            "access_token": access_token,
        },
        timeout=30,
    )
    publish_payload = _ensure_ok(publish_response, "Instagram Graph publish failed")
    media_id = publish_payload.get("id")
    if not media_id:
        raise InstagramGraphUploadError("Instagram Graph publish did not return media id")

    return str(media_id)
