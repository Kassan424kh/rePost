# rePost

Telegram bot that accepts a YouTube Shorts link and reuploads the same video to your YouTube channel as a Short.

## Setup

1. Create a Telegram bot and add it as an admin to your channel.
2. Create a Google Cloud project with YouTube Data API v3 enabled.
3. Download OAuth client credentials (Desktop app) as `credentials.json` and place it in the project root.
4. Copy `.env.example` to `.env` and fill the values.
5. Install dependencies.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python -m app.main
```

On first run, you will be prompted to authorize the YouTube account.

## Notes

- The bot only reacts to messages posted in the configured channel.
- The description suffix defaults to `#shorts` to keep uploads categorized as Shorts.
# rePost
