import asyncio
import logging

from dotenv import load_dotenv

from .config import Config
from .telegram_bot import build_app


def main() -> None:
    load_dotenv()

    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(name)s %(message)s", level=logging.INFO
    )

    config = Config.from_env()
    app = build_app(config)
    asyncio.set_event_loop(asyncio.new_event_loop())
    app.run_polling(close_loop=False)


if __name__ == "__main__":
    main()
