"""Thin wrapper around qbittorrent-api with torrent-state helpers."""

import qbittorrentapi

DOWNLOADING_STATES = {
    "downloading",
    "metaDL",
    "stalledDL",
    "queuedDL",
    "forcedDL",
    "checkingDL",
    "allocating",
}

SEEDING_STATES = {
    "uploading",
    "stalledUP",
    "queuedUP",
    "forcedUP",
    "pausedUP",
    "checkingUP",
}


def connect(host: str, port: int, username: str, password: str) -> qbittorrentapi.Client:
    client = qbittorrentapi.Client(
        host=host,
        port=port,
        username=username,
        password=password,
    )
    client.auth_log_in()
    return client


def is_downloading(torrent) -> bool:
    return torrent.state in DOWNLOADING_STATES


def is_complete(torrent) -> bool:
    return torrent.progress >= 1.0


def is_seeding(torrent) -> bool:
    return torrent.state in SEEDING_STATES


def add_torrent(client, urls: str) -> bool:
    result = client.torrents_add(urls=urls)
    return result == "Ok"
