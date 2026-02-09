from __future__ import annotations

from pathlib import Path
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def _load_credentials(
    client_secrets_path: str, token_path: str, oauth_flow: str
) -> Credentials:
    creds: Optional[Credentials] = None
    token_file = Path(token_path)
    if token_file.exists():
        creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    elif not creds:
        flow = InstalledAppFlow.from_client_secrets_file(client_secrets_path, SCOPES)
        if oauth_flow == "console":
            creds = flow.run_console()
        else:
            creds = flow.run_local_server(port=0)

    token_file.write_text(creds.to_json())
    return creds


def upload_short(
    *,
    file_path: Path,
    title: str,
    description: str,
    privacy_status: str,
    category_id: str,
    made_for_kids: bool,
    client_secrets_path: str,
    token_path: str,
    oauth_flow: str,
) -> str:
    creds = _load_credentials(client_secrets_path, token_path, oauth_flow)
    youtube = build("youtube", "v3", credentials=creds)

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "categoryId": category_id,
        },
        "status": {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": made_for_kids,
        },
    }

    media = MediaFileUpload(str(file_path), chunksize=-1, resumable=True)
    request = youtube.videos().insert(part=",".join(body.keys()), body=body, media_body=media)

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            pass

    return response.get("id")
