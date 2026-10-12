"""Telegram command handlers."""

import asyncio

from telegram import MessageEntity, Update
from telegram.ext import ContextTypes

from . import qbit_client
from .formatting import chunk_messages, format_downloading_line, format_seeding_line

HELP_TEXT = (
    "*qBittorrent notifier*\n\n"
    "/status — currently downloading torrents\n"
    "/seeding — currently seeding torrents\n"
    "/help — this message\n\n"
    "Send a magnet link or `.torrent` URL to queue a download."
)


def _authorized(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    chat = update.effective_chat
    return chat is not None and chat.id == context.bot_data["authorized_chat_id"]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _authorized(update, context):
        return
    await update.message.reply_text(HELP_TEXT, parse_mode="Markdown")


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _authorized(update, context):
        return

    client = context.bot_data["client"]
    torrents = await asyncio.to_thread(client.torrents_info)
    downloading = [t for t in torrents if qbit_client.is_downloading(t)]

    if not downloading:
        await update.message.reply_text("Nothing downloading right now.")
        return

    for chunk in chunk_messages([format_downloading_line(t) for t in downloading]):
        await update.message.reply_text(chunk, parse_mode="Markdown")


async def seeding(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _authorized(update, context):
        return

    client = context.bot_data["client"]
    torrents = await asyncio.to_thread(client.torrents_info)
    seeds = [t for t in torrents if qbit_client.is_seeding(t)]

    if not seeds:
        await update.message.reply_text("Nothing seeding right now.")
        return

    for chunk in chunk_messages([format_seeding_line(t) for t in seeds]):
        await update.message.reply_text(chunk, parse_mode="Markdown")


async def queue_torrent(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _authorized(update, context):
        return

    message = update.message
    url_map = message.parse_entities(types=[MessageEntity.URL])
    if not url_map:
        return

    urls = list(url_map.values())
    client = context.bot_data["client"]

    ok = await asyncio.to_thread(qbit_client.add_torrent, client, "\n".join(urls))
    if not ok:
        await message.reply_text("❌ Failed to queue torrent.")
        return

    first = urls[0]
    label = first[:60] + ("…" if len(first) > 60 else "")
    count = len(urls)
    header = f"✅ Queued {count} torrent{'s' if count > 1 else ''}: `{label}`"

    torrents = await asyncio.to_thread(client.torrents_info)
    downloading = [t for t in torrents if qbit_client.is_downloading(t)]

    if not downloading:
        await message.reply_text(f"{header}\n\nNo active downloads yet.", parse_mode="Markdown")
        return

    await message.reply_text(header, parse_mode="Markdown")
    for chunk in chunk_messages([format_downloading_line(t) for t in downloading]):
        await message.reply_text(chunk, parse_mode="Markdown")
