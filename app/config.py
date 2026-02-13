from dataclasses import dataclass
import os


def _get_bool(value: str, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y"}


@dataclass(frozen=True)
class Config:
    telegram_bot_token: str
    telegram_channel_id: int
    enable_youtube_upload: bool
    enable_tiktok_upload: bool
    enable_instagram_upload: bool
    youtube_client_secrets_path: str
    youtube_token_path: str
    youtube_privacy_status: str
    youtube_title_prefix: str
    youtube_description_suffix: str
    youtube_category_id: str
    youtube_made_for_kids: bool
    youtube_oauth_flow: str
    tiktok_access_token: str
    tiktok_privacy_level: str
    tiktok_disable_comment: bool
    tiktok_disable_duet: bool
    tiktok_disable_stitch: bool
    instagram_username: str
    instagram_password: str
    instagram_session_path: str
    instagram_caption_suffix: str
    download_dir: str
    allow_duplicate_uploads: bool

    @staticmethod
    def from_env() -> "Config":
        bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
        channel_id_raw = os.environ.get("TELEGRAM_CHANNEL_ID", "").strip()
        if not bot_token or not channel_id_raw:
            raise ValueError("Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHANNEL_ID.")

        return Config(
            telegram_bot_token=bot_token,
            telegram_channel_id=int(channel_id_raw),
            enable_youtube_upload=_get_bool(
                os.environ.get("ENABLE_YOUTUBE_UPLOAD"), True
            ),
            enable_tiktok_upload=_get_bool(
                os.environ.get("ENABLE_TIKTOK_UPLOAD"), False
            ),
            enable_instagram_upload=_get_bool(
                os.environ.get("ENABLE_INSTAGRAM_UPLOAD"), False
            ),
            youtube_client_secrets_path=os.environ.get(
                "YOUTUBE_CLIENT_SECRETS_PATH", "credentials.json"
            ),
            youtube_token_path=os.environ.get("YOUTUBE_TOKEN_PATH", "token.json"),
            youtube_privacy_status=os.environ.get("YOUTUBE_PRIVACY_STATUS", "public"),
            youtube_title_prefix=os.environ.get("YOUTUBE_TITLE_PREFIX", ""),
            youtube_description_suffix=os.environ.get(
                "YOUTUBE_DESCRIPTION_SUFFIX", "#shorts"
            ),
            youtube_category_id=os.environ.get("YOUTUBE_CATEGORY_ID", "22"),
            youtube_made_for_kids=_get_bool(
                os.environ.get("YOUTUBE_MADE_FOR_KIDS"), False
            ),
            youtube_oauth_flow=os.environ.get("YOUTUBE_OAUTH_FLOW", "local_server"),
            tiktok_access_token=os.environ.get("TIKTOK_ACCESS_TOKEN", "").strip(),
            tiktok_privacy_level=os.environ.get(
                "TIKTOK_PRIVACY_LEVEL", "PUBLIC_TO_EVERYONE"
            ),
            tiktok_disable_comment=_get_bool(
                os.environ.get("TIKTOK_DISABLE_COMMENT"), False
            ),
            tiktok_disable_duet=_get_bool(
                os.environ.get("TIKTOK_DISABLE_DUET"), False
            ),
            tiktok_disable_stitch=_get_bool(
                os.environ.get("TIKTOK_DISABLE_STITCH"), False
            ),
            instagram_username=os.environ.get("INSTAGRAM_USERNAME", "").strip(),
            instagram_password=os.environ.get("INSTAGRAM_PASSWORD", "").strip(),
            instagram_session_path=os.environ.get(
                "INSTAGRAM_SESSION_PATH", "instagram_session.json"
            ),
            instagram_caption_suffix=os.environ.get(
                "INSTAGRAM_CAPTION_SUFFIX", "#reels"
            ),
            download_dir=os.environ.get("DOWNLOAD_DIR", "downloads"),
            allow_duplicate_uploads=_get_bool(
                os.environ.get("ALLOW_DUPLICATE_UPLOADS"), False
            ),
        )
