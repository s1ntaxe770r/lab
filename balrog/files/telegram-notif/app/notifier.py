"""Background job: notify on Telegram when torrents finish downloading."""

import asyncio
import json
import logging
from pathlib import Path

from telegram.ext import ContextTypes

from . import qbit_client
from .formatting import human_size

logger = logging.getLogger(__name__)


def _load_notified(path: Path) -> set[str] | None:
    """Returns None if no state file exists yet (first run)."""
    if not path.exists():
        return None
    try:
        return set(json.loads(path.read_text()).get("notified", []))
    except (json.JSONDecodeError, OSError):
        return set()


def _save_notified(path: Path, notified: set[str]) -> None:
    path.write_text(json.dumps({"notified": sorted(notified)}))


async def check_completions(context: ContextTypes.DEFAULT_TYPE) -> None:
    job_data = context.job.data
    client = job_data["client"]
    chat_id = job_data["chat_id"]
    state_path: Path = job_data["state_path"]

    try:
        torrents = await asyncio.to_thread(client.torrents_info)
    except Exception:
        logger.exception("Failed to fetch torrents from qBittorrent")
        return

    completed_now = {t.hash for t in torrents if qbit_client.is_complete(t)}
    existing_hashes = {t.hash for t in torrents}

    notified = _load_notified(state_path)
    if notified is None:
        # First run: treat anything already complete as seen, so we don't
        # spam notifications for the existing library.
        _save_notified(state_path, completed_now)
        return

    new_completions = [t for t in torrents if t.hash in completed_now - notified]
    for torrent in new_completions:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"✅ Finished: *{torrent.name}* ({human_size(torrent.size)})",
            parse_mode="Markdown",
        )

    updated = (notified | completed_now) & existing_hashes
    if updated != notified:
        _save_notified(state_path, updated)
