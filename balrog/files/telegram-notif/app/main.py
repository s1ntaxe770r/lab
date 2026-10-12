"""Entry point: runs the Telegram bot and the qBittorrent completion poller."""

import logging
import os
from pathlib import Path

import httpx
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from telegram.request import HTTPXRequest

from . import handlers, qbit_client
from .notifier import check_completions

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    level=logging.INFO,
)


def main() -> None:
    qbit = qbit_client.connect(
        host=os.environ["QBIT_HOST"],
        port=int(os.environ["QBIT_PORT"]),
        username=os.environ["QBIT_USERNAME"],
        password=os.environ["QBIT_PASSWORD"],
    )

    chat_id = int(os.environ["TELEGRAM_CHAT_ID"])
    poll_interval = int(os.environ.get("POLL_INTERVAL_SECONDS", "30"))
    state_path = Path(os.environ.get("STATE_FILE", "state.json"))

    # api.telegram.org resolves to an IPv6 address with no working route on
    # this host, which stalls every request for several seconds before it
    # falls back to IPv4. Binding the local address to 0.0.0.0 forces httpx
    # to connect over IPv4.
    transport = httpx.AsyncHTTPTransport(local_address="0.0.0.0")
    request = HTTPXRequest(httpx_kwargs={"transport": transport})

    application = (
        ApplicationBuilder()
        .token(os.environ["TELEGRAM_BOT_TOKEN"])
        .request(request)
        .get_updates_request(request)
        .build()
    )

    application.bot_data["client"] = qbit
    application.bot_data["authorized_chat_id"] = chat_id

    application.add_handler(CommandHandler(["start", "help"], handlers.start))
    application.add_handler(CommandHandler("status", handlers.status))
    application.add_handler(CommandHandler("seeding", handlers.seeding))
    application.add_handler(MessageHandler(filters.Entity("url"), handlers.queue_torrent))

    application.job_queue.run_repeating(
        check_completions,
        interval=poll_interval,
        first=10,
        data={"client": qbit, "chat_id": chat_id, "state_path": state_path},
    )

    application.run_polling()


if __name__ == "__main__":
    main()
