import logging
import re
from pathlib import Path
from typing import Optional

from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

from .config import Config
from .downloader import download_short
from .youtube import upload_short

YOUTUBE_URL_RE = re.compile(
    r"(?:https?://)?(?:www\.)?(?:youtube\.com/shorts/|youtu\.be/)([A-Za-z0-9_-]{6,})"
)


def extract_video_id(text: str) -> Optional[str]:
    match = YOUTUBE_URL_RE.search(text)
    if not match:
        return None
    return match.group(1)


def _build_title(info: dict, prefix: str) -> str:
    base = info.get("title") or "YouTube Short"
    if prefix:
        return f"{prefix} {base}".strip()
    return base


def _build_description(info: dict, suffix: str) -> str:
    base = info.get("description") or ""
    parts = [base.strip(), suffix.strip()]
    return "\n\n".join([p for p in parts if p])


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    config: Config = context.application.bot_data["config"]

    msg = update.channel_post or update.message
    if not msg or msg.chat_id != config.telegram_channel_id:
        return

    if not msg.text:
        return

    video_id = extract_video_id(msg.text)
    if not video_id:
        return

    url = f"https://youtube.com/shorts/{video_id}"
    await context.bot.send_message(
        chat_id=config.telegram_channel_id,
        text="Downloading and uploading the Short. This may take a few minutes...",
    )

    file_path: Path | None = None
    try:
        file_path, info = download_short(url, config.download_dir)
        title = _build_title(info, config.youtube_title_prefix)
        description = _build_description(info, config.youtube_description_suffix)
        upload_id = upload_short(
            file_path=file_path,
            title=title,
            description=description,
            privacy_status=config.youtube_privacy_status,
            category_id=config.youtube_category_id,
            made_for_kids=config.youtube_made_for_kids,
            client_secrets_path=config.youtube_client_secrets_path,
            token_path=config.youtube_token_path,
            oauth_flow=config.youtube_oauth_flow,
        )
    except Exception as exc:
        logging.exception("Failed to process short")
        await context.bot.send_message(
            chat_id=config.telegram_channel_id,
            text=f"Failed to upload the Short: {exc}",
        )
        return
    finally:
        if file_path and file_path.exists():
            file_path.unlink()
            logging.info("Deleted downloaded file: %s", file_path)

    await context.bot.send_message(
        chat_id=config.telegram_channel_id,
        text=f"Uploaded Short: https://youtu.be/{upload_id}",
    )


def build_app(config: Config):
    app = ApplicationBuilder().token(config.telegram_bot_token).build()
    app.bot_data["config"] = config

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    return app
