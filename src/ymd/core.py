"""
Основной модуль с логикой загрузки и обработки треков.
"""

import datetime as dt
import hashlib
import os
import re
import subprocess
import time
import typing
import logging
from collections.abc import Callable
from dataclasses import dataclass
from enum import IntEnum, auto
from pathlib import Path
from typing import Optional, Union

import mutagen
from mutagen.flac import FLAC, Picture
from mutagen.id3._frames import (
    APIC,
    TALB,
    TCON,
    TDRC,
    TIT2,
    TPE1,
    TPE2,
    TPOS,
    TRCK,
    USLT,
    WOAF,
)
from mutagen.id3._specs import ID3TimeStamp, PictureType
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4, MP4Cover
from strenum import LowercaseStrEnum
from yandex_music import (
    Album,
    Client,
    Track,
    YandexMusicModel,
)
from yandex_music.exceptions import NetworkError

from ymd import api, text_utils
from ymd.api import (
    ApiTrackQuality,
    Container,
    Codec,
    CustomDownloadInfo,
    get_download_info,
)
from ymd.mime_utils import MimeType, guess_mime_type

logger = logging.getLogger(__name__)

# Константы
UNSAFE_PATH_CLEAR_RE = re.compile(r"[/\\]+")
SAFE_PATH_CLEAR_RE = re.compile(r"([^\w\-\'() ]|^\s+|\s+$)")

DEFAULT_PATH_PATTERN = Path("#album-artist", "#album", "#number - #title")
DEFAULT_COVER_RESOLUTION = 400

MIN_COMPATIBILITY_LEVEL = 0
MAX_COMPATIBILITY_LEVEL = 1

AUDIO_FILE_SUFFIXES = {".mp3", ".flac", ".m4a"}
TEMPORARY_FILE_NAME_TEMPLATE = ".yandex-music-downloader.{}.tmp"
MAX_FILE_NAME_BYTE_LENGTH_WITHOUT_SUFFIX = 255 - max(
    len(suffix) for suffix in AUDIO_FILE_SUFFIXES
)


class CoreTrackQuality:
    """
    Качество трека для внутреннего использования.
    Может быть числовым (0, 1, 2) или битрейтом (192, 256, 320).
    """
    def __init__(self, value: Union[int, str]):
        self.value = value if isinstance(value, int) else int(value)
    
    @property
    def is_lossless(self) -> bool:
        return self.value == 2
    
    @property
    def is_mp3_bitrate(self) -> bool:
        return self.value in (192, 256, 320)
    
    @property
    def is_aac_quality(self) -> bool:
        return self.value in (0, 1)
    
    @property
    def bitrate(self) -> Optional[int]:
        return self.value if self.is_mp3_bitrate else None
    
    @property
    def api_quality(self) -> ApiTrackQuality:
        if self.value == 0:
            return ApiTrackQuality.LOW
        elif self.value == 1:
            return ApiTrackQuality.NORMAL
        else:  # 2, 192, 256, 320
            return ApiTrackQuality.LOSSLESS
    
    @property
    def suffix(self) -> str:
        if self.is_lossless:
            return ".flac"
        elif self.is_mp3_bitrate:
            return ".mp3"
        elif self.is_aac_quality:
            return ".m4a"
        else:
            return ".m4a"


class LyricsFormat(LowercaseStrEnum):
    """Форматы текстов песен."""
    NONE = auto()
    TEXT = auto()
    LRC = auto()


# Маппинг контейнеров для mutagen
CONTAINER_MUTAGEN_MAPPING: dict[Container, type[mutagen.FileType]] = {
    Container.MP3: MP3,
    Container.FLAC: FLAC,
    Container.MP4: MP4,
}


@dataclass
class DownloadableTrack:
    """Трек, готовый к скачиванию."""
    download_info: CustomDownloadInfo
    path: Path
    track: Track
    quality: CoreTrackQuality


@dataclass
class AlbumCover:
    """Обложка альбома."""
    data: bytes
    mime_type: MimeType


def debug_print(debug: bool, msg: str, data: any = None):
    """Вывод отладочной информации."""
    if debug:
        print(f"  [DEBUG core] {msg}")
        if data is not None:
            print(f"  [DEBUG core] {data}")


def init_client(
    token: str, timeout: int, max_try_count: int, retry_delay: int
) -> Client:
    """
    Инициализирует клиент Яндекс.Музыки с повторными попытками.
    
    Args:
        token: Токен авторизации
        timeout: Таймаут запросов
        max_try_count: Максимальное количество попыток (0 - бесконечно)
        retry_delay: Задержка между попытками
        
    Returns:
        Client: Инициализированный клиент
    """
    assert timeout > 0
    assert max_try_count >= 0
    assert retry_delay >= 0

    client = Client(token)
    client.request.set_timeout(timeout)

    original_wrapper = client.request._request_wrapper

    def retry_wrapper(*args, **kwargs):
        try_count = 0
        while True:
            try:
                return original_wrapper(*args, **kwargs)
            except NetworkError as error:
                if max_try_count == 0 or try_count < max_try_count:
                    try_count += 1
                    time.sleep(retry_delay)
                    continue
                raise error

    client.request._request_wrapper = retry_wrapper
    return client.init()


def full_title(obj: YandexMusicModel) -> str:
    """Возвращает полное название с версией."""
    result = obj["title"]
    if result is None:
        return ""
    if version := obj["version"]:
        result += f" ({version})"
    return result


def prepare_base_path(
    path_pattern: Path, track: Track, unsafe_path: bool = False, debug: bool = False
) -> Path:
    """
    Подготавливает путь для сохранения трека, заменяя плейсхолдеры.
    
    Args:
        path_pattern: Шаблон пути с плейсхолдерами
        track: Объект трека
        unsafe_path: Разрешить небезопасные символы
        debug: Режим отладки
        
    Returns:
        Path: Подготовленный путь
    """
    debug_print(debug, f"prepare_base_path: path_pattern={path_pattern}, track.title={track.title}")
    
    path_str = str(path_pattern)
    album = None
    album_artist = None
    track_artist = None
    track_position = None
    
    if albums := track.albums:
        album = albums[0]
        track_position = album.track_position
        if artists := album.artists:
            album_artist = artists[0]
    
    if artists := track.artists:
        track_artist = artists[0]
    
    repl_dict: dict[str, Union[str, int, None]] = {
        "#number-padded": str(track_position.index).zfill(len(str(album.track_count)))
        if track_position and album else None,
        "#album-artist": album_artist.name if album_artist else None,
        "#track-artist": track_artist.name if track_artist else None,
        "#artist-id": track_artist.id if track_artist else None,
        "#album-id": album.id if album else None,
        "#track-id": track.id,
        "#number": track_position.index if track_position else None,
        "#title": full_title(track),
        "#album": full_title(album) if album else None,
        "#year": album.year if album else None,
    }
    
    for placeholder, replacement in repl_dict.items():
        replacement = str(replacement)
        if not unsafe_path:
            clear_re = SAFE_PATH_CLEAR_RE
        else:
            clear_re = UNSAFE_PATH_CLEAR_RE
        replacement = clear_re.sub("_", replacement)
        path_str = path_str.replace(placeholder, replacement)
    
    path = Path(path_str)
    
    # Обрезаем слишком длинные имена
    trimmed_parts = [
        part[:MAX_FILE_NAME_BYTE_LENGTH_WITHOUT_SUFFIX]
        if len(part) > MAX_FILE_NAME_BYTE_LENGTH_WITHOUT_SUFFIX else part
        for part in path.parts
    ]
    result = Path(*trimmed_parts)
    debug_print(debug, f"prepare_base_path: result={result}")
    return result


def set_tags(
    path: Path,
    track: Track,
    container: Container,
    lyrics: Optional[str],
    album_cover: Optional[AlbumCover],
    compatibility_level: int,
) -> None:
    """
    Устанавливает теги аудиофайла.
    
    Args:
        path: Путь к файлу
        track: Объект трека
        container: Тип контейнера
        lyrics: Текст песни
        album_cover: Обложка альбома
        compatibility_level: Уровень совместимости
    """
    file_type = CONTAINER_MUTAGEN_MAPPING.get(container)
    if file_type is None:
        raise ValueError(f"Unknown container: {container}")

    tag = file_type(path)
    album = track.albums[0] if track.albums else Album()
    album_title = full_title(album)
    track_title = full_title(track)
    track_artists = [a.name for a in track.artists if a.name]
    album_artists = [a.name for a in album.artists if a.name]
    genre = album.genre if album.genre else None
    track_number = None
    disc_number = None
    
    if position := album.track_position:
        track_number = position.index
        disc_number = position.volume
    
    iso8601_release_date = None
    release_year: Optional[str] = None
    
    if album.release_date is not None:
        iso8601_release_date = dt.datetime.fromisoformat(album.release_date).astimezone(
            dt.timezone.utc
        )
        release_year = str(iso8601_release_date.year)
        iso8601_release_date = iso8601_release_date.strftime("%Y-%m-%d %H:%M:%S")
    
    if year := album.year:
        release_year = str(year)
    
    track_url = f"https://music.yandex.ru/album/{album.id}/track/{track.id}"

    if isinstance(tag, MP3):
        _set_mp3_tags(
            tag, track_title, album_title, track_artists, album_artists,
            iso8601_release_date, release_year, track_number, disc_number,
            genre, lyrics, album_cover, track_url
        )
    elif isinstance(tag, MP4):
        _set_mp4_tags(
            tag, track_title, album_title, track_artists, album_artists,
            iso8601_release_date, release_year, track_number, disc_number,
            genre, lyrics, album_cover, track_url, compatibility_level
        )
    elif isinstance(tag, FLAC):
        _set_flac_tags(
            tag, track_title, album_title, track_artists, album_artists,
            iso8601_release_date, release_year, track_number, disc_number,
            genre, lyrics, album_cover, track_url
        )
    else:
        raise RuntimeError("Unknown file format")

    tag.save()


def _set_mp3_tags(tag, track_title, album_title, track_artists, album_artists,
                  iso8601_release_date, release_year, track_number, disc_number,
                  genre, lyrics, album_cover, track_url):
    """Устанавливает теги для MP3."""
    tag["TIT2"] = TIT2(encoding=3, text=track_title)
    tag["TALB"] = TALB(encoding=3, text=album_title)
    tag["TPE1"] = TPE1(encoding=3, text=track_artists)
    tag["TPE2"] = TPE2(encoding=3, text=album_artists)

    if tdrc_text := iso8601_release_date or release_year:
        tag["TDRC"] = TDRC(encoding=3, text=[ID3TimeStamp(tdrc_text)])
    if track_number:
        tag["TRCK"] = TRCK(encoding=3, text=str(track_number))
    if disc_number:
        tag["TPOS"] = TPOS(encoding=3, text=str(disc_number))
    if genre:
        tag["TCON"] = TCON(encoding=3, text=genre)

    if lyrics:
        tag["USLT"] = USLT(encoding=3, text=lyrics)
    if album_cover:
        tag["APIC"] = APIC(
            encoding=3,
            mime=album_cover.mime_type.value,
            type=3,
            data=album_cover.data,
        )

    tag["WOAF"] = WOAF(encoding=3, text=track_url)


def _set_mp4_tags(tag, track_title, album_title, track_artists, album_artists,
                  iso8601_release_date, release_year, track_number, disc_number,
                  genre, lyrics, album_cover, track_url, compatibility_level):
    """Устанавливает теги для MP4."""
    tag["\xa9nam"] = track_title
    tag["\xa9alb"] = album_title
    
    artists_value = "; ".join(track_artists) if compatibility_level == 1 else track_artists
    album_artists_value = "; ".join(album_artists) if compatibility_level == 1 else album_artists
    
    tag["\xa9ART"] = artists_value
    tag["aART"] = album_artists_value

    if iso8601_release_date is not None:
        tag["\xa9day"] = iso8601_release_date
    elif release_year is not None:
        tag["\xa9day"] = release_year
    
    if track_number:
        tag["trkn"] = [(track_number, 0)]
    if disc_number:
        tag["disk"] = [(disc_number, 0)]
    if genre:
        tag["\xa9gen"] = genre

    if lyrics:
        tag["\xa9lyr"] = lyrics
    if album_cover:
        mime_mp4_dict = {
            MimeType.JPEG: MP4Cover.FORMAT_JPEG,
            MimeType.PNG: MP4Cover.FORMAT_PNG,
        }
        mp4_image_format = mime_mp4_dict.get(album_cover.mime_type)
        if mp4_image_format is None:
            raise RuntimeError("Unsupported cover type")
        tag["covr"] = [MP4Cover(album_cover.data, imageformat=mp4_image_format)]
    
    tag["\xa9cmt"] = track_url


def _set_flac_tags(tag, track_title, album_title, track_artists, album_artists,
                   iso8601_release_date, release_year, track_number, disc_number,
                   genre, lyrics, album_cover, track_url):
    """Устанавливает теги для FLAC."""
    tag["title"] = track_title
    tag["album"] = album_title
    tag["artist"] = track_artists
    tag["albumartist"] = album_artists

    if date_text := iso8601_release_date or release_year:
        tag["date"] = date_text
    if track_number:
        tag["tracknumber"] = str(track_number)
    if disc_number:
        tag["discnumber"] = str(disc_number)
    if genre:
        tag["genre"] = genre

    if lyrics:
        tag["lyrics"] = lyrics
    if album_cover is not None:
        pic = Picture()
        pic.type = PictureType.COVER_FRONT
        pic.data = album_cover.data
        pic.mime = album_cover.mime_type.value
        tag.add_picture(pic)
    
    tag["comment"] = track_url


def download_track(
    track_info: DownloadableTrack,
    cover_resolution: Union[int, str] = DEFAULT_COVER_RESOLUTION,
    lyrics_format: LyricsFormat = LyricsFormat.NONE,
    embed_cover: bool = False,
    covers_cache: Optional[dict[int, AlbumCover]] = None,
    compatibility_level: int = 1,
    debug: bool = False,
    force_mp3: bool = False,
) -> None:
    """
    Скачивает и обрабатывает трек.
    
    Args:
        track_info: Информация о треке для скачивания
        cover_resolution: Разрешение обложки
        lyrics_format: Формат текста песни
        embed_cover: Встраивать обложку в файл
        covers_cache: Кэш обложек
        compatibility_level: Уровень совместимости
        debug: Режим отладки
        force_mp3: Принудительная конвертация AAC в MP3 для качества 0 и 1
    """
    if embed_cover and covers_cache is None:
        raise RuntimeError("covers_cache isn't provided")
    covers_cache = typing.cast(dict[int, AlbumCover], covers_cache)
    
    target_path = track_info.path
    track = track_info.track
    quality = track_info.quality
    client = typing.cast(Client, track.client)
    assert client

    debug_print(
        debug,
        f"download_track: target_path={target_path}, quality={quality.value}",
    )

    debug_print(debug, "Получение текста песни...")
    text_lyrics = _get_lyrics(
        track,
        lyrics_format,
        target_path,
        debug,
    )
    debug_print(debug, "Текст песни обработан")

    debug_print(debug, "Загрузка обложки...")
    cover = _get_album_cover(
        track,
        cover_resolution,
        embed_cover,
        covers_cache,
        target_path,
        debug,
    )
    debug_print(debug, "Обложка обработана")

    debug_print(debug, "Получение аудиоданных...")
    download_info = track_info.download_info
    track_data = api.download_track(
        client,
        download_info,
    )
    debug_print(
        debug,
        f"Аудиоданные получены: {len(track_data)} bytes",
    )

    # Обрабатываем файл
    def process_hook(tmp_path: Path) -> Path:
        return _process_file_hook(
            tmp_path, target_path, download_info, quality,
            track, text_lyrics, cover, compatibility_level, debug, force_mp3
        )

    debug_print(
        debug,
        "Запись и обработка файла..."
    )

    # Сохраняем файл
    write_via_temporary_file(
        track_data,
        target_path,
        temporary_file_hook=process_hook,
        debug=debug,
    )

    debug_print(
        debug,
        "Файл обработан и сохранён"
    )


def _get_lyrics(track: Track, lyrics_format: LyricsFormat, target_path: Path, debug: bool) -> Optional[str]:
    """Получает текст песни в нужном формате."""
    text_lyrics = None
    if lyrics_format != LyricsFormat.NONE and (lyrics_info := track.lyrics_info):
        if lyrics_format == LyricsFormat.LRC and lyrics_info.has_available_sync_lyrics:
            lrc_path = target_path.with_suffix(".lrc")
            if not lrc_path.is_file() and (track_lyrics := track.get_lyrics(format_="LRC")):
                lyrics = track_lyrics.fetch_lyrics()
                write_via_temporary_file(lyrics.encode("utf-8"), lrc_path, debug=debug)
        elif lyrics_info.has_available_text_lyrics:
            if track_lyrics := track.get_lyrics(format_="TEXT"):
                text_lyrics = track_lyrics.fetch_lyrics()
    return text_lyrics


def _get_album_cover(track: Track, cover_resolution: Union[int, str], embed_cover: bool,
                     covers_cache: dict[int, AlbumCover], target_path: Path, debug: bool) -> Optional[AlbumCover]:
    """Получает обложку альбома."""
    cover = None
    if track.cover_uri is not None:
        cover_size = "orig" if cover_resolution in (-1, "original") else f"{cover_resolution}x{cover_resolution}"
        cover_bytes = track.download_cover_bytes(size=cover_size)
        mime_type = guess_mime_type(cover_bytes)
        if mime_type is None:
            raise RuntimeError("Unknown cover mime type")
        
        album_cover = AlbumCover(data=cover_bytes, mime_type=mime_type)
        
        if embed_cover:
            album = track.albums[0] if track.albums else Album()
            if album.id and (cached_cover := covers_cache.get(album.id)):
                cover = cached_cover
            elif album.id:
                cover = covers_cache[album.id] = album_cover
        else:
            mime_suffix_dict = {MimeType.JPEG: ".jpg", MimeType.PNG: ".png"}
            file_suffix = mime_suffix_dict.get(album_cover.mime_type)
            if file_suffix is None:
                raise RuntimeError("Unknown mime type")
            cover_path = target_path.parent / ("cover" + file_suffix)
            if not cover_path.is_file():
                write_via_temporary_file(album_cover.data, cover_path, debug=debug)
    return cover


def _process_file_hook(tmp_path: Path, target_path: Path, download_info: CustomDownloadInfo,
                       quality: CoreTrackQuality, track: Track, 
                       text_lyrics: Optional[str], cover: Optional[AlbumCover],
                       compatibility_level: int, debug: bool, force_mp3: bool = False) -> Path:
    """
    Обрабатывает скачанный файл: конвертирует, добавляет теги.
    """
    container = download_info.file_format.container
    codec = download_info.file_format.codec
    final_path = target_path
    bitrate = download_info.bitrate
    
    need_conversion = False
    convert_to = None
    mp3_bitrate = None
    
    debug_print(debug, f"_process_file_hook: container={container}, codec={codec}, bitrate={bitrate}, target_path.suffix={target_path.suffix}, quality.value={quality.value}, force_mp3={force_mp3}")
    
    # Случай 1: FLAC в MP4 -> настоящий FLAC (только для качества 2)
    if container == Container.MP4 and codec == Codec.FLAC and quality.is_lossless and target_path.suffix == ".flac":
        need_conversion = True
        convert_to = "flac"
        logger.debug(
            "FLAC in MP4 container; converting to FLAC"
        )
    
    # Случай 2: FLAC в MP4 -> MP3 (для битрейтов 192, 256, 320)
    elif container == Container.MP4 and codec == Codec.FLAC and quality.is_mp3_bitrate:
        need_conversion = True
        convert_to = "mp3"
        mp3_bitrate = quality.bitrate
        logger.debug(
            "FLAC in MP4 container; converting to MP3 %s kbps",
            mp3_bitrate
        )
    
    # Случай 3: AAC в MP4 -> MP3 (для битрейтов 192, 256, 320 или FLAC)
    elif container == Container.MP4 and codec == Codec.AAC and quality.is_mp3_bitrate:
        need_conversion = True
        convert_to = "mp3"
        mp3_bitrate = quality.bitrate
        logger.debug(
            "Converting AAC to MP3 %s kbps",
            mp3_bitrate
        )
    
    # Случай 4: FLAC в MP4 -> MP3 (для качества 2 если target_path .mp3)
    elif container == Container.MP4 and codec == Codec.FLAC and target_path.suffix == ".mp3":
        need_conversion = True
        convert_to = "mp3"
        mp3_bitrate = quality.bitrate
        logger.debug(
            "FLAC in MP4 container; converting to MP3 %s kbps",
            mp3_bitrate
        )
    
    # Случай 5: AAC в MP4 -> MP3 при force_mp3 (для качества 0 и 1)
    elif container == Container.MP4 and codec == Codec.AAC and force_mp3 and quality.is_aac_quality:
        need_conversion = True
        convert_to = "mp3"
        if quality.value == 0:
            mp3_bitrate = 64
        else:  # quality.value == 1
            mp3_bitrate = 192
        logger.debug(
            "Forced conversion of AAC to MP3 %s kbps",
            mp3_bitrate
        )
    
    # Случай 6: MP3 контейнер -> если запрошен FLAC или MP3 с другим битрейтом, просто сохраняем
    # В этом случае конвертация не нужна, файл уже MP3
    
    if need_conversion:
        tmp_path, container, final_path = _convert_file(
            tmp_path, target_path, convert_to, container, mp3_bitrate, debug
        )

    # Добавляем теги
    debug_print(debug, f"set_tags: container={container}, final_path={final_path}")
    set_tags(
        tmp_path,
        track,
        container,
        text_lyrics,
        cover,
        compatibility_level,
    )

    return final_path


def _convert_file(tmp_path: Path, target_path: Path, convert_to: str, 
                  container: Container, mp3_bitrate: Optional[int], debug: bool) -> tuple[Path, Container, Path]:
    """Конвертирует файл с помощью ffmpeg."""
    try:
        subprocess.run(["ffmpeg", "-version"],
                       capture_output=True,
                       check=True,
                       timeout=10,
                       creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
                       )
        debug_print(debug, f"ffmpeg найден, запускаем конвертацию")
        
        if convert_to == "flac":
            output_tmp = tmp_path.with_suffix(".flac")
            debug_print(debug, f"Конвертация FLAC: {tmp_path} -> {output_tmp}")
            subprocess.run([
                "ffmpeg",
                "-nostdin",
                "-y",
                "-i", str(tmp_path),
                "-vn",
                "-c:a", "copy",
                "-map_metadata", "-1",
                str(output_tmp),
            ],
                check=True,
                capture_output=True,
                timeout=180,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )
            output_tmp.replace(tmp_path)
            container = Container.FLAC
            logger.debug(
                "Successfully converted to FLAC"
            )
            
        elif convert_to == "mp3" and mp3_bitrate:
            output_tmp = tmp_path.with_suffix(".mp3")
            debug_print(debug, f"Конвертация MP3: {tmp_path} -> {output_tmp}, битрейт={mp3_bitrate}")
            subprocess.run([
                "ffmpeg",
                "-nostdin",
                "-y",
                "-i", str(tmp_path),
                "-vn",
                "-c:a", "libmp3lame",
                "-b:a", f"{mp3_bitrate}k",
                "-map_metadata", "-1",
                str(output_tmp),
            ],
                check=True,
                capture_output=True,
                timeout=180,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )
            output_tmp.replace(tmp_path)
            container = Container.MP3
            final_path = target_path.with_suffix('.mp3')
            target_path = final_path
            logger.debug(
                "Successfully converted to MP3 (%s kbps)",
                mp3_bitrate
            )
            
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError) as e:
        error_msg = f"Ошибка ffmpeg: {e}" if isinstance(e, subprocess.CalledProcessError) else "ffmpeg не найден"
        logger.debug(
            "  ⚠️ %s",
            error_msg
        )
        logger.debug(
            "Save in the original format"
        )
        if target_path.suffix == ".flac":
            final_path = target_path.with_suffix('.m4a')
            target_path = final_path
            tmp_path.rename(final_path)
            tmp_path = final_path
            container = Container.MP4
    
    return tmp_path, container, target_path


def _get_target_bitrate(requested: Optional[int], available: int, default: int = 256) -> int:
    """
    Определяет целевой битрейт для конвертации.
    
    Args:
        requested: Запрошенный битрейт (может быть None)
        available: Доступный битрейт исходного файла
        default: Битрейт по умолчанию, если available = 0
        
    Returns:
        int: Целевой битрейт
    """
    if available > 0:
        if requested is not None:
            target = min(requested, available)
        else:
            target = available
    else:
        target = default if requested is None else requested
    
    # Округляем до стандартного значения
    standard_bitrates = [64, 128, 160, 192, 256, 320]
    return min(standard_bitrates, key=lambda x: abs(x - target))


def to_downloadable_track(
    track: Track, quality_value: Union[int, str], base_path: Path, debug: bool = False, force_mp3: bool = False
) -> DownloadableTrack:
    """
    Преобразует трек в объект для скачивания.
    
    Args:
        track: Объект трека
        quality_value: Запрашиваемое качество (0, 1, 2, 192, 256, 320)
        base_path: Базовый путь без расширения
        debug: Режим отладки
        force_mp3: Принудительная конвертация AAC в MP3 для качества 0 и 1
        
    Returns:
        DownloadableTrack: Объект с информацией для скачивания
    """
    quality = CoreTrackQuality(quality_value)
    
    debug_print(debug, f"to_downloadable_track: base_path={base_path}, quality={quality.value}, force_mp3={force_mp3}")

    
    download_info = get_download_info(track, quality.api_quality)
    container = download_info.file_format.container
    codec = download_info.file_format.codec
    bitrate = download_info.bitrate

    logger.debug(
        "API response: container=%s, codec=%s, bitrate=%s",
        container.value,
        codec.value,
        bitrate,
    )

    # Определяем расширение файла и качество для конвертации
    if quality.is_mp3_bitrate:
        # Запрошен MP3 с конкретным битрейтом
        if codec == Codec.FLAC:
            # FLAC -> MP3 с запрошенным битрейтом
            target_bitrate = quality.bitrate
            suffix = ".mp3"
            logger.debug(
                "FLAC will be converted to MP3 %s kbps",
                target_bitrate
            )
        elif codec == Codec.AAC:
            # AAC -> MP3 с минимальным из {запрошенный, исходный}
            target_bitrate = _get_target_bitrate(quality.bitrate, bitrate)
            quality = CoreTrackQuality(target_bitrate)
            suffix = ".mp3"
            logger.debug(
                "AAC will be converted to MP3 %s kbps",
                target_bitrate
            )
        elif codec == Codec.MP3:
            # Уже MP3, сохраняем как есть
            suffix = ".mp3"
            if bitrate > 0:
                logger.debug(
                    "   Save the MP3 as-is (specified by API: %s kbps)",
                    bitrate
                )
            else:
                logger.debug(
                    "   Save the MP3 as-is"
                )
        else:
            suffix = ".mp3"
            
    elif quality.is_lossless:
        # Запрошен FLAC
        if codec == Codec.FLAC:
            suffix = ".flac"
        elif codec == Codec.AAC:
            # FLAC недоступен, конвертируем AAC в MP3 с битрейтом исходного AAC
            target_bitrate = _get_target_bitrate(None, bitrate, default=256)
            quality = CoreTrackQuality(target_bitrate)
            suffix = ".mp3"
            logger.debug(
                "FLAC is not available, AAC will be converted to MP3 %s kbps",
                target_bitrate
            )
        elif codec == Codec.MP3:
            # FLAC недоступен, сохраняем MP3 как есть
            suffix = ".mp3"
            if bitrate > 0:
                logger.debug(
                    "FLAC is not available, save the MP3 as-is (specified by API: %s kbps)",
                    bitrate
                )
            else:
                logger.debug(
                    "FLAC is not available, save the MP3 as-is"
                )
        else:
            suffix = ".flac"
    else:
        # Качество 0 или 1 (AAC)
        if force_mp3:
            # Принудительная конвертация в MP3
            target_bitrate = 64 if quality.value == 0 else 192
            quality = CoreTrackQuality(target_bitrate)
            suffix = ".mp3"
            logger.debug(
                "   Forced Conversion of AAC to MP3 %s kbps",
                target_bitrate
            )
        else:
            suffix = ".m4a"
            logger.debug(
                "   Save as M4A (AAC %s kbps)",
                bitrate
            )

    logger.debug(
        "Output extension: %s",
        suffix,
    )

    target_path = str(base_path) + suffix
    debug_print(debug, f"to_downloadable_track: target_path={target_path}")
    
    return DownloadableTrack(
        download_info=download_info,
        track=track,
        path=Path(target_path),
        quality=quality,
    )


def write_via_temporary_file(
    data: bytes,
    target_path: Path,
    temporary_file_hook: Optional[Callable[[Path], Path]] = None,
    debug: bool = False,
) -> Path:
    """
    Записывает данные во временный файл, затем переименовывает.
    
    Args:
        data: Данные для записи
        target_path: Конечный путь
        temporary_file_hook: Функция для обработки временного файла
        debug: Режим отладки
        
    Returns:
        Path: Путь к сохраненному файлу
    """
    target_name = hashlib.sha256(target_path.name.encode()).hexdigest()
    temporary_file = target_path.parent / (
        TEMPORARY_FILE_NAME_TEMPLATE.format(target_name)
    )
    debug_print(debug, f"write_via_temporary_file: target_path={target_path}, temporary_file={temporary_file}")
    
    try:
        temporary_file.write_bytes(data)
        if temporary_file_hook is not None:
            final_file = temporary_file_hook(temporary_file)
            debug_print(debug, f"write_via_temporary_file: final_file после хука={final_file}")
        else:
            final_file = target_path
    except InterruptedError as e:
        temporary_file.unlink()
        raise e

    if temporary_file.exists():
        debug_print(debug, f"write_via_temporary_file: переименовываем {temporary_file} -> {final_file}")
        temporary_file.replace(final_file)

    debug_print(debug, f"write_via_temporary_file: результат={final_file}")
    return final_file