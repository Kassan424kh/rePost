# rePost

Telegram bot that accepts a YouTube Shorts link and reuploads the same video to YouTube, TikTok, and Instagram.

## Setup

Use Python `3.13` (recommended) for dependency compatibility.

1. Create a Telegram bot and add it as an admin to your channel.
2. Create a Google Cloud project with YouTube Data API v3 enabled.
3. Download OAuth client credentials (Desktop app) as `credentials.json` and place it in the project root (if using YouTube upload).
4. Copy `.env.example` to `.env` and fill the values.
5. Install dependencies.

```bash
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python -m app.main
```

On first run, you will be prompted to authorize the YouTube account.

## Environment variables

### Required

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHANNEL_ID`

### Platform toggles

- `ENABLE_YOUTUBE_UPLOAD=true`
- `ENABLE_TIKTOK_UPLOAD=false`
- `ENABLE_INSTAGRAM_UPLOAD=false`

### YouTube

- `YOUTUBE_CLIENT_SECRETS_PATH=credentials.json`
- `YOUTUBE_TOKEN_PATH=token.json`
- `YOUTUBE_PRIVACY_STATUS=public`
- `YOUTUBE_TITLE_PREFIX=`
- `YOUTUBE_DESCRIPTION_SUFFIX=#shorts`
- `YOUTUBE_CATEGORY_ID=22`
- `YOUTUBE_MADE_FOR_KIDS=false`
- `YOUTUBE_OAUTH_FLOW=local_server`

### TikTok (Content Posting API)

- `TIKTOK_ACCESS_TOKEN=...`
- `TIKTOK_PRIVACY_LEVEL=PUBLIC_TO_EVERYONE`
- `TIKTOK_DISABLE_COMMENT=false`
- `TIKTOK_DISABLE_DUET=false`
- `TIKTOK_DISABLE_STITCH=false`

### Instagram

- `INSTAGRAM_USERNAME=...`
- `INSTAGRAM_PASSWORD=...`
- `INSTAGRAM_SESSION_PATH=instagram_session.json`
- `INSTAGRAM_CAPTION_SUFFIX=#reels`

## Notes

- The bot only reacts to messages posted in the configured channel.
- The same downloaded video file is reused for all enabled platforms.
- TikTok uploads require a valid user access token from TikTok's API.
- Instagram uploads use account login via `instagrapi`; first login may require verification/challenge handling.
