import logging
import re
from pathlib import Path
from typing import Optional

from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

from .config import Config
from .downloader import download_short
from .instagram import upload_reel
from .tiktok import upload_video as upload_tiktok_video
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


def _build_caption(info: dict, suffix: str) -> str:
    base = info.get("description") or info.get("title") or ""
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
        caption = _build_caption(info, config.instagram_caption_suffix)

        results: list[str] = []
        failures: list[str] = []

        if config.enable_youtube_upload:
            try:
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
                results.append(f"YouTube: https://youtu.be/{upload_id}")
            except Exception as exc:
                logging.exception("YouTube upload failed")
                failures.append(f"YouTube: {exc}")

        if config.enable_tiktok_upload:
            if not config.tiktok_access_token:
                failures.append("TikTok: missing TIKTOK_ACCESS_TOKEN")
            else:
                try:
                    publish_id = upload_tiktok_video(
                        file_path=file_path,
                        title=title,
                        access_token=config.tiktok_access_token,
                        privacy_level=config.tiktok_privacy_level,
                        disable_comment=config.tiktok_disable_comment,
                        disable_duet=config.tiktok_disable_duet,
                        disable_stitch=config.tiktok_disable_stitch,
                    )
                    results.append(f"TikTok publish id: {publish_id}")
                except Exception as exc:
                    logging.exception("TikTok upload failed")
                    failures.append(f"TikTok: {exc}")

        if config.enable_instagram_upload:
            if not config.instagram_username or not config.instagram_password:
                failures.append("Instagram: missing INSTAGRAM_USERNAME or INSTAGRAM_PASSWORD")
            else:
                try:
                    media_id = upload_reel(
                        file_path=file_path,
                        caption=caption,
                        username=config.instagram_username,
                        password=config.instagram_password,
                        session_path=config.instagram_session_path,
                    )
                    results.append(f"Instagram reel media id: {media_id}")
                except Exception as exc:
                    logging.exception("Instagram upload failed")
                    failures.append(f"Instagram: {exc}")

        if not results and failures:
            raise RuntimeError("; ".join(failures))

        response_lines = []
        if results:
            response_lines.append("Upload results:")
            response_lines.extend(results)
        if failures:
            response_lines.append("")
            response_lines.append("Failed:")
            response_lines.extend(failures)

        if response_lines:
            await context.bot.send_message(
                chat_id=config.telegram_channel_id,
                text="\n".join(response_lines),
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


def build_app(config: Config):
    app = ApplicationBuilder().token(config.telegram_bot_token).build()
    app.bot_data["config"] = config

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    return app
