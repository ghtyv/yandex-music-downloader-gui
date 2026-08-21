from __future__ import annotations

import copy
import itertools
import logging
import re
import subprocess
import threading
import time
from concurrent.futures import (
    FIRST_COMPLETED,
    Future,
    ThreadPoolExecutor,
    wait,
)
from dataclasses import dataclass
from pathlib import Path
from typing import Callable
from urllib.parse import urlparse

from yandex_music import Album, Client, Track
from yandex_music.exceptions import (
    NetworkError,
    UnauthorizedError,
)

from ymd import core as ymd_core
from ymd.cli import get_playlist_info_from_uuid


LogCallback = Callable[[str], None]
ProgressCallback = Callable[[int, int], None]
StatusCallback = Callable[[str], None]
CancelCallback = Callable[[], bool]

logger = logging.getLogger(__name__)


DEFAULT_PARALLEL_DOWNLOADS = 3
MIN_PARALLEL_DOWNLOADS = 1
MAX_PARALLEL_DOWNLOADS = 8

TRACK_RE = re.compile(r"track/(\d+)")
ALBUM_RE = re.compile(r"album/(\d+)$")
ARTIST_RE = re.compile(r"artist/(\d+)$")
PLAYLIST_RE = re.compile(r"([\w\-._@]+)/playlists/(\d+)$")
PLAYLIST_UUID_RE = re.compile(r"playlists/([0-9A-Za-z\-_.]+)$")


@dataclass
class DownloadConfig:
    token: str
    url: str
    output_dir: Path
    quality: int = 2

    path_pattern: Path = Path(
        "#album-artist - #title #track-id"
    )

    skip_existing: bool = True
    embed_cover: bool = True
    cover_resolution: int = 400

    delay: int = 0

    timeout: int = 20
    tries: int = 2
    retry_delay: int = 2

    compatibility_level: int = 1
    force_mp3: bool = False
    debug: bool = False
    parallel_downloads: int = DEFAULT_PARALLEL_DOWNLOADS


@dataclass
class DownloadStats:
    total: int = 0
    downloaded: int = 0
    skipped: int = 0
    unavailable: int = 0
    errors: int = 0


@dataclass
class TrackTask:
    number: int
    total: int
    track: Track
    artists: str
    title: str
    prefix: str
    downloadable: ymd_core.DownloadableTrack


class DownloadCancelled(Exception):
    pass


class Downloader:
    def __init__(
        self,
        log_callback: LogCallback | None = None,
        progress_callback: ProgressCallback | None = None,
        status_callback: StatusCallback | None = None,
        cancel_callback: CancelCallback | None = None,
    ):
        self.log_callback = log_callback
        self.progress_callback = progress_callback
        self.status_callback = status_callback
        self.cancel_callback = cancel_callback

    def log(self, message: str):
        if self.log_callback:
            self.log_callback(message)

    def progress(self, current: int, total: int):
        if self.progress_callback:
            self.progress_callback(current, total)

    def status(self, message: str):
        if self.status_callback:
            self.status_callback(message)

    @staticmethod
    def _clamp_parallel_downloads(
        value: int,
    ) -> int:
        return max(
            MIN_PARALLEL_DOWNLOADS,
            min(MAX_PARALLEL_DOWNLOADS, value),
        )

    @staticmethod
    def _build_client(
        config: DownloadConfig,
    ) -> Client:
        client = ymd_core.init_client(
            token=config.token,
            timeout=config.timeout,
            max_try_count=config.tries,
            retry_delay=config.retry_delay,
        )
        client.token = config.token
        return client

    def create_client(self, config: DownloadConfig) -> Client:
        self.status("Подключение к Яндекс Музыке...")
        self.log("Подключение к Яндекс Музыке...")

        client = self._build_client(config)

        self.log("Авторизация выполнена.")
        return client

    @staticmethod
    def _fetch_tracks_by_ids(
        client: Client,
        track_ids: list,
    ) -> list[Track]:
        result: list[Track] = []

        for offset in range(0, len(track_ids), 50):
            batch = track_ids[offset:offset + 50]
            tracks = client.tracks(batch)

            if tracks:
                result.extend(
                    track
                    for track in tracks
                    if track is not None
                )

        return result

    def _get_playlist_tracks(
        self,
        client: Client,
        playlist_id: str,
    ) -> list[Track]:
        if playlist_id.startswith("liked/"):
            self.log('Получение плейлиста "Мне нравится"...')

            likes = client.users_likes_tracks()

            if not likes:
                return []

            track_ids = [
                item.id
                for item in likes
                if getattr(item, "id", None) is not None
            ]

            return self._fetch_tracks_by_ids(
                client,
                track_ids,
            )

        owner, kind = playlist_id.split("/", 1)

        self.log(
            f"Получение плейлиста {owner}/{kind}..."
        )

        playlist = client.users_playlists(
            kind,
            owner,
        )

        if playlist is None:
            raise RuntimeError(
                "Плейлист не найден."
            )

        track_ids = []

        for item in getattr(playlist, "tracks", []):
            track = getattr(item, "track", None)

            if track is not None:
                track_id = getattr(track, "id", None)

                if track_id is None and isinstance(track, dict):
                    track_id = track.get("id")
            else:
                track_id = getattr(item, "id", None)

                if track_id is None and isinstance(item, dict):
                    track_id = item.get("id")

            if track_id is not None:
                track_ids.append(track_id)

        return self._fetch_tracks_by_ids(
            client,
            track_ids,
        )

    def resolve_url(
        self,
        client: Client,
        url: str,
        debug: bool = False,
    ) -> list[Track]:
        parsed = urlparse(url)
        path = parsed.path.rstrip("/")

        if match := TRACK_RE.search(path):
            track_id = match.group(1)
            tracks = client.tracks(track_id)

            if not tracks:
                raise RuntimeError("Трек не найден.")

            if isinstance(tracks, list):
                return tracks

            return [tracks]

        if match := ALBUM_RE.search(path):
            album_id = match.group(1)
            album = client.albums_with_tracks(
                album_id
            )

            if not album or not album.volumes:
                raise RuntimeError(
                    "Альбом не найден или пуст."
                )

            return list(
                itertools.chain.from_iterable(
                    album.volumes
                )
            )

        if match := ARTIST_RE.search(path):
            artist_id = match.group(1)
            tracks: list[Track] = []
            page = 0

            while True:
                result = client.artists_direct_albums(
                    artist_id,
                    page,
                )

                if not result:
                    break

                albums: list[Album] = result.albums or []

                for album in albums:
                    if (
                        album.id is None
                        or not album.available
                    ):
                        continue

                    full_album = client.albums_with_tracks(
                        album.id
                    )

                    if full_album and full_album.volumes:
                        tracks.extend(
                            itertools.chain.from_iterable(
                                full_album.volumes
                            )
                        )

                pager = result.pager

                if pager is None:
                    break

                page = pager.page + 1

                if pager.per_page * page >= pager.total:
                    break

            return tracks

        if match := PLAYLIST_UUID_RE.search(path):
            playlist_uuid = match.group(1)

            self.log(
                f"Обнаружен UUID плейлиста: "
                f"{playlist_uuid}"
            )

            playlist_id = get_playlist_info_from_uuid(
                client,
                playlist_uuid,
                debug,
            )

            if playlist_id is None:
                raise RuntimeError(
                    "Не удалось получить информацию "
                    "о плейлисте."
                )

            return self._get_playlist_tracks(
                client,
                playlist_id,
            )

        if match := PLAYLIST_RE.search(path):
            playlist_id = (
                f"{match.group(1)}/{match.group(2)}"
            )

            return self._get_playlist_tracks(
                client,
                playlist_id,
            )

        raise ValueError(
            "Неподдерживаемый формат ссылки "
            "Яндекс Музыки."
        )

    @staticmethod
    def _track_artists(track: Track) -> str:
        artists = getattr(track, "artists", []) or []

        return ", ".join(
            getattr(artist, "name", None)
            or artist.get("name", "")
            if isinstance(artist, dict)
            else getattr(artist, "name", "")
            for artist in artists
        )

    @staticmethod
    def _already_exists(base_path: Path) -> bool:
        parent = base_path.parent

        if not parent.is_dir():
            return False

        for file in parent.iterdir():
            if (
                file.is_file()
                and file.stem == base_path.name
            ):
                return True

        return False

    def _prepare_track_tasks(
        self,
        tracks: list[Track],
        config: DownloadConfig,
        stats: DownloadStats,
    ) -> tuple[list[TrackTask], int]:
        tasks: list[TrackTask] = []
        completed = 0

        for number, track in enumerate(
            tracks,
            start=1,
        ):
            self.check_cancelled()

            title = track.title or "Без названия"
            artists = self._track_artists(track)
            prefix = f"[{number}/{stats.total}]"

            if not track.available:
                stats.unavailable += 1
                completed += 1

                self.log(
                    f"{prefix} Недоступен: "
                    f"{artists} - {title}"
                )
                self.progress(
                    completed,
                    stats.total,
                )
                continue

            base_path = (
                config.output_dir
                / ymd_core.prepare_base_path(
                    config.path_pattern,
                    track,
                    False,
                    config.debug,
                )
            )

            if (
                config.skip_existing
                and self._already_exists(base_path)
            ):
                stats.skipped += 1
                completed += 1

                self.status(
                    f"Пропуск {number}/{stats.total}: "
                    f"{artists} — {title}"
                )
                self.log(
                    f"{prefix} Уже существует: "
                    f"{artists} - {title}"
                )
                self.progress(
                    completed,
                    stats.total,
                )
                continue

            base_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            downloadable = ymd_core.to_downloadable_track(
                track,
                config.quality,
                base_path,
                config.debug,
                config.force_mp3,
            )

            tasks.append(
                TrackTask(
                    number=number,
                    total=stats.total,
                    track=track,
                    artists=artists,
                    title=title,
                    prefix=prefix,
                    downloadable=downloadable,
                )
            )

        return tasks, completed

    def _download_track_task(
        self,
        task: TrackTask,
        config: DownloadConfig,
        cover_cache: dict[int, ymd_core.AlbumCover],
        cover_cache_lock: threading.Lock,
    ) -> str:
        task_client = self._build_client(config)

        task_track = copy.copy(task.track)
        task_track.client = task_client

        task_downloadable = copy.copy(
            task.downloadable
        )
        task_downloadable.track = task_track

        if config.embed_cover:
            with cover_cache_lock:
                local_cover_cache = dict(cover_cache)
        else:
            local_cover_cache = {}

        ymd_core.download_track(
            track_info=task_downloadable,
            lyrics_format=ymd_core.LyricsFormat.NONE,
            embed_cover=config.embed_cover,
            cover_resolution=config.cover_resolution,
            covers_cache=local_cover_cache,
            compatibility_level=(
                config.compatibility_level
            ),
            debug=config.debug,
            force_mp3=config.force_mp3,
        )

        if config.embed_cover:
            with cover_cache_lock:
                cover_cache.update(local_cover_cache)

        return task_downloadable.path.name

    def _download_parallel(
        self,
        tasks: list[TrackTask],
        config: DownloadConfig,
        stats: DownloadStats,
        completed: int,
    ) -> None:
        max_workers = self._clamp_parallel_downloads(
            config.parallel_downloads
        )

        self.log(
            "Параллельных загрузок: "
            f"{max_workers}"
        )

        cover_cache: dict[int, ymd_core.AlbumCover] = {}
        cover_cache_lock = threading.Lock()

        executor = ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix="ymd-download",
        )
        futures: dict[Future[str], TrackTask] = {}
        pending: set[Future[str]] = set()
        fatal_error: BaseException | None = None
        cancellation_requested = False

        try:
            for task in tasks:
                self.check_cancelled()

                self.status(
                    f"Очередь {task.number}/{task.total}: "
                    f"{task.artists} — {task.title}"
                )
                self.log(
                    f"{task.prefix} Запуск: "
                    f"{task.artists} - {task.title}"
                )

                future = executor.submit(
                    self._download_track_task,
                    task,
                    config,
                    cover_cache,
                    cover_cache_lock,
                )
                futures[future] = task
                pending.add(future)

                if config.delay > 0:
                    time.sleep(config.delay)

            while pending:
                if (
                    not cancellation_requested
                    and self.cancel_callback is not None
                    and self.cancel_callback()
                ):
                    cancellation_requested = True

                    self.status(
                        "Остановка запрошена. "
                        "Ожидание активных задач..."
                    )

                    for future in list(pending):
                        future.cancel()

                done, pending = wait(
                    pending,
                    timeout=0.2,
                    return_when=FIRST_COMPLETED,
                )

                for future in done:
                    task = futures[future]

                    if future.cancelled():
                        continue

                    try:
                        file_name = future.result()

                    except DownloadCancelled as error:
                        cancellation_requested = True

                        if fatal_error is None:
                            fatal_error = error

                    except UnauthorizedError as error:
                        logger.warning(
                            "OAuth token rejected while processing track"
                        )
                        cancellation_requested = True

                        if fatal_error is None:
                            fatal_error = error

                    except NetworkError:
                        stats.errors += 1
                        completed += 1

                        logger.exception(
                            "Network error for track: %s - %s",
                            task.artists,
                            task.title,
                        )
                        self.log(
                            f"{task.prefix} Ошибка сети: "
                            f"{task.artists} - {task.title}"
                        )
                        self.progress(
                            completed,
                            stats.total,
                        )

                    except subprocess.TimeoutExpired:
                        stats.errors += 1
                        completed += 1

                        logger.exception(
                            "FFmpeg timeout for track: %s - %s",
                            task.artists,
                            task.title,
                        )
                        self.log(
                            f"{task.prefix} FFmpeg не успел "
                            f"обработать трек: "
                            f"{task.artists} - {task.title}"
                        )
                        self.progress(
                            completed,
                            stats.total,
                        )

                    except PermissionError:
                        stats.errors += 1
                        completed += 1

                        logger.exception(
                            "Permission error for track: %s - %s",
                            task.artists,
                            task.title,
                        )
                        self.log(
                            f"{task.prefix} Нет доступа "
                            f"к файлу: "
                            f"{task.artists} - {task.title}"
                        )
                        self.progress(
                            completed,
                            stats.total,
                        )

                    except Exception as error:
                        stats.errors += 1
                        completed += 1

                        logger.exception(
                            "Track processing failed: %s - %s",
                            task.artists,
                            task.title,
                        )
                        self.log(
                            f"{task.prefix} Ошибка: "
                            f"{task.artists} - {task.title}: {error}"
                        )
                        self.progress(
                            completed,
                            stats.total,
                        )

                    else:
                        stats.downloaded += 1
                        completed += 1

                        self.log(
                            f"{task.prefix} Готово: "
                            f"{file_name}"
                        )
                        self.progress(
                            completed,
                            stats.total,
                        )

                    if (
                        cancellation_requested
                        or fatal_error is not None
                    ):
                        for pending_future in list(
                            pending
                        ):
                            pending_future.cancel()
                    else:
                        self.status(
                            f"Обработано "
                            f"{completed}/{stats.total}"
                        )

            if fatal_error is not None:
                raise fatal_error

            if cancellation_requested:
                raise DownloadCancelled()

        finally:
            executor.shutdown(
                wait=True,
                cancel_futures=True,
            )

    def download(
        self,
        config: DownloadConfig,
    ) -> DownloadStats:
        client = self.create_client(config)

        self.status("Получение списка треков...")
        self.log("Получение списка треков...")

        tracks = self.resolve_url(
            client,
            config.url,
            config.debug,
        )

        stats = DownloadStats(
            total=len(tracks)
        )

        self.status(
            f"Найдено треков: {stats.total}"
        )
        self.log(
            f"Найдено треков: {stats.total}"
        )

        tasks, completed = self._prepare_track_tasks(
            tracks,
            config,
            stats,
        )

        self._download_parallel(
            tasks,
            config,
            stats,
            completed,
        )

        self.status("Загрузка завершена")
        self.log(
            "Загрузка завершена. "
            f"Скачано: {stats.downloaded}; "
            f"пропущено: {stats.skipped}; "
            f"недоступно: {stats.unavailable}; "
            f"ошибок: {stats.errors}."
        )

        return stats

    def check_cancelled(self):
        if (
            self.cancel_callback is not None
            and self.cancel_callback()
        ):
            raise DownloadCancelled()
