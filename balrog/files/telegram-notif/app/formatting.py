"""Helpers for turning torrent info into Telegram-friendly text."""

# qBittorrent uses this as a sentinel for "unknown/infinite" ETA
_ETA_INFINITE = 8640000


def human_size(num_bytes: float) -> str:
    size = float(num_bytes)
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if size < 1024 or unit == "TiB":
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TiB"


def human_speed(bytes_per_sec: float) -> str:
    return f"{human_size(bytes_per_sec)}/s"


def human_eta(seconds: int) -> str:
    if seconds is None or seconds >= _ETA_INFINITE:
        return "∞"
    seconds = int(seconds)
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours}h{minutes:02d}m"
    if minutes:
        return f"{minutes}m{secs:02d}s"
    return f"{secs}s"


def progress_bar(fraction: float, width: int = 10) -> str:
    fraction = max(0.0, min(1.0, fraction))
    filled = round(fraction * width)
    return "[" + ("█" * filled) + ("-" * (width - filled)) + f"] {fraction * 100:.0f}%"


def format_downloading_line(torrent) -> str:
    return (
        f"\U0001f4e5 *{torrent.name}*\n"
        f"{progress_bar(torrent.progress)}\n"
        f"{human_speed(torrent.dlspeed)} — ETA {human_eta(torrent.eta)}"
    )


def format_seeding_line(torrent) -> str:
    return (
        f"\U0001f331 *{torrent.name}*\n"
        f"Size: {human_size(torrent.size)} — Ratio: {torrent.ratio:.2f}\n"
        f"Uploaded: {human_size(torrent.uploaded)} — {human_speed(torrent.upspeed)}"
    )


def chunk_messages(parts: list[str], max_length: int = 3500) -> list[str]:
    """Join `parts` with blank lines, splitting into chunks under Telegram's message limit."""
    chunks: list[str] = []
    current = ""
    for part in parts:
        candidate = f"{current}\n\n{part}" if current else part
        if len(candidate) > max_length and current:
            chunks.append(current)
            current = part
        else:
            current = candidate
    if current:
        chunks.append(current)
    return chunks
