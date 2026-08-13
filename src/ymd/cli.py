#!/bin/python3
"""
Главный исполняемый модуль для скачивания музыки с Яндекс.Музыки.
Поддерживает загрузку треков, альбомов, плейлистов и избранного.
"""

import argparse
import itertools
import logging
import re
import time
import json
from argparse import ArgumentTypeError
from collections.abc import Callable, Generator, Iterable
from pathlib import Path
from typing import Optional, Union
from urllib.parse import urlparse
from datetime import datetime

from yandex_music import Album, Track, Playlist

from ymd import core

DEFAULT_DELAY = 0

TRACK_RE = re.compile(r"track/(\d+)")
ALBUM_RE = re.compile(r"album/(\d+)$")
ARTIST_RE = re.compile(r"artist/(\d+)$")
PLAYLIST_RE = re.compile(r"([\w\-._@]+)/playlists/(\d+)$")
PLAYLIST_UUID_RE = re.compile(r"playlists/([0-9A-Za-z\-_.]+)$")

FETCH_PAGE_SIZE = 10

logger = logging.getLogger("yandex-music-downloader")


def debug_print(debug: bool, msg: str):
    """Вывод отладочной информации."""
    if debug:
        print(f"[DEBUG cli] {msg}")


def show_default(text: Optional[str] = None) -> str:
    """Форматирует сообщение с значением по умолчанию."""
    default = "по умолчанию: %(default)s"
    return default if text is None else f"{text} ({default})"


def quality_arg(astr: str) -> int:
    """
    Проверяет аргумент качества.
    Поддерживает: 0, 1, 2, 192, 256, 320
    """
    try:
        value = int(astr)
        valid_values = [0, 1, 2, 192, 256, 320]
        if value in valid_values:
            return value
        else:
            raise ArgumentTypeError(
                f"Недопустимое значение: {value}. "
                f"Допустимые значения: {', '.join(map(str, valid_values))}"
            )
    except ValueError:
        raise ArgumentTypeError(f"Значение должно быть числом: {astr}")


def cover_resolution_arg(astr: str) -> int:
    """Проверяет аргумент разрешения обложки."""
    return -1 if astr == "original" else checked_int_arg(100)(astr)


def checked_int_arg(min_value: int, max_value: Optional[int] = None) -> Callable[[str], int]:
    """Создает функцию проверки целочисленного аргумента."""
    def func(astr: str) -> int:
        aint = int(astr)
        if aint >= min_value and (max_value is None or aint <= max_value):
            return aint
        error_text = f"Значение должен быть >= {min_value}"
        if max_value is not None:
            error_text += f" и <= {max_value}"
        raise ArgumentTypeError(error_text)
    return func


def lyrics_format_arg(astr: str) -> core.LyricsFormat:
    """Проверяет аргумент формата текста песни."""
    try:
        return core.LyricsFormat(astr)
    except ValueError:
        raise ArgumentTypeError(f"Допустимые значения: {','.join(core.LyricsFormat)}")


def get_artists(track: Track) -> str:
    """Возвращает список исполнителей трека в виде строки."""
    return ", ".join(map(lambda x: x['name'], track.artists))


def get_playlist_info_from_uuid(client, uuid: str, debug: bool = False) -> Optional[str]:
    """
    Получает информацию о плейлисте по UUID.
    
    Args:
        client: Клиент Яндекс.Музыки
        uuid: UUID плейлиста
        debug: Режим отладки
        
    Returns:
        Optional[str]: Строка вида "owner/kind" или None
    """
    try:
        debug_print(debug, f"get_playlist_info_from_uuid: uuid={uuid}")
        print(f"  Получаем плейлист через API...")
        
        # Проверяем, не является ли плейлист "Мне нравится"
        if uuid.startswith('lk.'):
            debug_print(debug, f"Обнаружен плейлист 'Мне нравится' (lk.)")
            print(f"  Обнаружен специальный плейлист 'Мне нравится'")
            return f"liked/{uuid}"
        
        # Сначала пробуем найти среди своих плейлистов
        try:
            user_playlists = client.users_playlists_list()
            debug_print(debug, f"Получено {len(user_playlists) if user_playlists else 0} своих плейлистов")
            if user_playlists:
                for playlist in user_playlists:
                    playlist_uuid = getattr(playlist, 'playlist_uuid', None)
                    if playlist_uuid == uuid:
                        owner = getattr(playlist, 'owner', {})
                        owner_login = owner.get('login') if isinstance(owner, dict) else getattr(owner, 'login', None)
                        kind = getattr(playlist, 'kind', None)
                        debug_print(debug, f"Найден свой плейлист: owner={owner_login}, kind={kind}")
                        if owner_login and kind:
                            print(f"  ✅ Найдено через users_playlists_list: owner={owner_login}, kind={kind}")
                            return f"{owner_login}/{kind}"
        except Exception as e:
            if debug:
                print(f"  [DEBUG] Ошибка users_playlists_list: {e}")
        
        # Если не нашли среди своих, пробуем получить через API с другим эндпоинтом
        try:
            debug_print(debug, "Пробуем получить публичный плейлист через API (альтернативный эндпоинт)")
            import requests
            # Используем эндпоинт, который возвращает информацию о плейлисте по UUID
            url = f"https://api.music.yandex.net/playlists/{uuid}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json',
                'Authorization': f'OAuth {client.token}'
            }
            response = requests.get(url, headers=headers, timeout=30)
            debug_print(debug, f"Статус ответа: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                debug_print(debug, f"Ответ: {json.dumps(data, indent=2)[:500]}...")
                if 'result' in data:
                    playlist = data['result']
                    owner = playlist.get('owner', {})
                    owner_login = owner.get('login') if isinstance(owner, dict) else owner
                    kind = playlist.get('kind')
                    if owner_login and kind:
                        print(f"  ✅ Найдено через публичный API: owner={owner_login}, kind={kind}")
                        return f"{owner_login}/{kind}"
            elif response.status_code == 404:
                debug_print(debug, "Плейлист не найден (404)")
            else:
                debug_print(debug, f"Ошибка: {response.status_code} - {response.text[:200]}")
        except Exception as e:
            if debug:
                print(f"  [DEBUG] Ошибка публичного API: {e}")
        
        # Если API не помог, пробуем получить информацию через метод playlist() с UUID
        try:
            debug_print(debug, "Пробуем получить через client.playlist() с UUID")
            # Пробуем разные форматы
            for fmt in [uuid, f"playlists/{uuid}", f"/playlists/{uuid}"]:
                try:
                    debug_print(debug, f"Пробуем формат: {fmt}")
                    playlist = client.playlist(fmt)
                    if playlist:
                        owner = getattr(playlist, 'owner', {})
                        owner_login = owner.get('login') if isinstance(owner, dict) else getattr(owner, 'login', None)
                        kind = getattr(playlist, 'kind', None)
                        if owner_login and kind:
                            print(f"  ✅ Найдено через client.playlist(): owner={owner_login}, kind={kind}")
                            return f"{owner_login}/{kind}"
                except Exception as e2:
                    debug_print(debug, f"Ошибка для формата {fmt}: {e2}")
        except Exception as e:
            if debug:
                print(f"  [DEBUG] Ошибка client.playlist(): {e}")
        
        # Если ничего не помогло, пробуем получить информацию из HTML-страницы
        try:
            debug_print(debug, "Пробуем получить информацию из HTML-страницы")
            import requests
            url = f"https://music.yandex.ru/playlists/{uuid}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            }
            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code == 200:
                html = response.text
                
                # Ищем iframe с ссылкой
                match = re.search(r'<iframe[^>]*src="https?://music\.yandex\.ru/iframe/playlist/([^"]+)"', html)
                if match:
                    playlist_path = match.group(1)
                    print(f"  ✅ Найдена ссылка в iframe: {playlist_path}")
                    return playlist_path
                
                # Ищем INITIAL_STATE
                match = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.*?});', html, re.DOTALL)
                if match:
                    data = json.loads(match.group(1))
                    
                    def find_playlist(obj, depth=0):
                        if depth > 15:
                            return None
                        if isinstance(obj, dict):
                            if 'playlist' in obj and isinstance(obj['playlist'], dict):
                                p = obj['playlist']
                                if 'kind' in p and 'owner' in p:
                                    return p
                            for key, value in obj.items():
                                if key in ['playlist', 'playlistPage']:
                                    result = find_playlist(value, depth + 1)
                                    if result:
                                        return result
                            for value in obj.values():
                                result = find_playlist(value, depth + 1)
                                if result:
                                    return result
                        elif isinstance(obj, list):
                            for item in obj:
                                result = find_playlist(item, depth + 1)
                                if result:
                                    return result
                        return None
                    
                    playlist = find_playlist(data)
                    if playlist:
                        owner = playlist.get('owner', {})
                        if isinstance(owner, dict):
                            owner_login = owner.get('login') or owner.get('uid')
                        else:
                            owner_login = owner
                        kind = playlist.get('kind') or playlist.get('id')
                        if owner_login and kind:
                            print(f"  ✅ Найдено через INITIAL_STATE: owner={owner_login}, kind={kind}")
                            return f"{owner_login}/{kind}"
                
                # Ищем прямую ссылку
                match = re.search(r'/users/([^/]+)/playlists/(\d+)', html)
                if match:
                    owner_login = match.group(1)
                    kind = match.group(2)
                    print(f"  ✅ Найдено через прямую ссылку: owner={owner_login}, kind={kind}")
                    return f"{owner_login}/{kind}"
                    
        except Exception as e:
            if debug:
                print(f"  [DEBUG] Ошибка парсинга HTML: {e}")
        
        print(f"  ❌ Не удалось получить информацию о плейлисте")
        return None
        
    except Exception as e:
        print(f"  ❌ Ошибка: {e}")
        if debug:
            import traceback
            traceback.print_exc()
        return None


def save_unavailable_tracks(unavailable_tracks: list, playlist_url: str, output_dir: Path):
    """Сохраняет список недоступных треков в файл."""
    if not unavailable_tracks:
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"unavailable_tracks_{timestamp}.txt"
    filepath = output_dir / filename
    
    lines = [
        "=" * 60,
        "СПИСОК НЕДОСТУПНЫХ ТРЕКОВ",
        f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Источник: {playlist_url}",
        f"Всего недоступно: {len(unavailable_tracks)}",
        "=" * 60,
        ""
    ]
    
    for i, track_info in enumerate(unavailable_tracks, 1):
        lines.append(f"{i:4}. {track_info['artists']} - {track_info['title']}")
        lines.append(f"     ID: {track_info['id']}")
        lines.append(f"     Альбом: {track_info['album']}")
        lines.append("")
    
    lines.extend(["=" * 60, f"Всего: {len(unavailable_tracks)} треков", "=" * 60])
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        print(f"\n📁 Список недоступных треков сохранен: {filepath}")
        print(f"   Всего: {len(unavailable_tracks)} треков")
    except Exception as e:
        print(f"  ⚠️ Ошибка при сохранении списка: {e}")


def save_tracks_list(tracks: Iterable[Track], output_dir: Path, source: str, total_count: Optional[int] = None):
    """
    Сохраняет список треков в текстовый файл.
    
    Args:
        tracks: Итератор с треками
        output_dir: Папка для сохранения
        source: Источник (URL или playlist_id)
        total_count: Общее количество треков (если известно)
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"tracks_list_{timestamp}.txt"
    filepath = output_dir / filename
    
    # Создаем папку, если её нет
    if not output_dir.is_dir():
        output_dir.mkdir(parents=True)
    
    lines = [
        "=" * 80,
        "СПИСОК ТРЕКОВ",
        f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Источник: {source}",
        f"Всего треков: {total_count if total_count is not None else 'неизвестно'}",
        "=" * 80,
        ""
    ]
    
    track_counter = 0
    unavailable_counter = 0
    
    for track in tracks:
        if not track.available:
            artists = get_artists(track)
            title = track.title
            lines.append(f"  🚫 {artists} - {title} (НЕДОСТУПЕН)")
            unavailable_counter += 1
            track_counter += 1
            continue
        
        # Формируем имя как #album-artist - #title
        try:
            if track.albums and track.albums[0].artists:
                # Получаем имя первого исполнителя из первого альбома
                artist_obj = track.albums[0].artists[0]
                # Проверяем, что это объект Artist, а не словарь
                if hasattr(artist_obj, 'name'):
                    album_artist = artist_obj.name
                elif isinstance(artist_obj, dict):
                    album_artist = artist_obj.get('name', 'Неизвестный исполнитель')
                else:
                    album_artist = 'Неизвестный исполнитель'
            else:
                album_artist = 'Неизвестный исполнитель'
        except (AttributeError, IndexError, TypeError):
            album_artist = 'Неизвестный исполнитель'
        
        title = track.title
        lines.append(f"  {album_artist} - {title}")
        track_counter += 1
    
    lines.extend(["=" * 80, f"Всего сохранено: {track_counter} треков", f"  🚫 Недоступно: {unavailable_counter}", "=" * 80])
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        print(f"\n📋 Список треков сохранен: {filepath}")
        print(f"   Всего треков: {track_counter}")
        print(f"   Из них недоступно: {unavailable_counter}")
    except Exception as e:
        print(f"  ⚠️ Ошибка при сохранении списка: {e}")


def check_bitrates(download_dir: Path, download_count: int, debug: bool = False):
    """
    Проверяет реальный битрейт загруженных MP3-файлов.
    
    Args:
        download_dir: Директория с загруженными файлами
        download_count: Количество загруженных файлов
        debug: Режим отладки
    """
    if download_count == 0:
        print("\n📊 Нет загруженных файлов для проверки битрейта")
        return
    
    print("\n🔍 ПРОВЕРКА РЕАЛЬНОГО БИТРЕЙТА MP3-ФАЙЛОВ...")
    print("=" * 60)
    
    try:
        import mutagen
        from mutagen.mp3 import MP3
        
        mp3_files = list(download_dir.glob("**/*.mp3"))
        
        if not mp3_files:
            print("⚠️ MP3-файлы не найдены в указанной директории")
            return
        
        print(f"Найдено MP3-файлов: {len(mp3_files)}")
        print()
        
        # Собираем статистику
        stats = {
            "total": 0,
            "by_bitrate": {},
            "suspicious": [],  # файлы с битрейтом ниже 192 kbps
        }
        
        for mp3_file in mp3_files:
            try:
                audio = MP3(mp3_file)
                bitrate = audio.info.bitrate // 1000  # Переводим в kbps
                
                stats["total"] += 1
                stats["by_bitrate"][bitrate] = stats["by_bitrate"].get(bitrate, 0) + 1
                
                # Проверяем, не слишком ли низкий битрейт для MP3
                # Для современных треков норма - 192+ kbps
                if bitrate < 192 and bitrate > 0:
                    stats["suspicious"].append({
                        "file": mp3_file.name,
                        "bitrate": bitrate,
                        "size_kb": mp3_file.stat().st_size // 1024
                    })
                    
            except Exception as e:
                if debug:
                    print(f"  ⚠️ Ошибка чтения {mp3_file.name}: {e}")
        
        # Выводим статистику
        print("📊 СТАТИСТИКА БИТРЕЙТОВ:")
        print("-" * 40)
        
        # Сортируем по битрейту
        for bitrate in sorted(stats["by_bitrate"].keys(), reverse=True):
            count = stats["by_bitrate"][bitrate]
            bar = "█" * min(count, 50)
            print(f"  {bitrate:3d} kbps: {count:3d} файлов {bar}")
        
        print("-" * 40)
        print(f"  Всего проверено: {stats['total']} файлов")
        
        # Предупреждения о подозрительных файлах
        if stats["suspicious"]:
            print("\n⚠️ ФАЙЛЫ С НИЗКИМ БИТРЕЙТОМ (< 192 kbps):")
            for item in stats["suspicious"][:10]:  # Показываем первые 10
                print(f"  {item['file']}")
                print(f"    Битрейт: {item['bitrate']} kbps, Размер: {item['size_kb']} KB")
            
            if len(stats["suspicious"]) > 10:
                print(f"  ... и еще {len(stats['suspicious']) - 10} файлов")
        else:
            print("\n✅ Все файлы имеют битрейт 192 kbps или выше!")
        
        # Сохраняем отчет
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = download_dir / f"bitrate_report_{timestamp}.txt"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("ОТЧЕТ ПО БИТРЕЙТАМ MP3-ФАЙЛОВ\n")
            f.write(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Директория: {download_dir}\n")
            f.write("=" * 60 + "\n\n")
            
            f.write("СТАТИСТИКА:\n")
            for bitrate in sorted(stats["by_bitrate"].keys(), reverse=True):
                count = stats["by_bitrate"][bitrate]
                f.write(f"  {bitrate:3d} kbps: {count:3d} файлов\n")
            
            f.write(f"\nВсего проверено: {stats['total']} файлов\n")
            
            if stats["suspicious"]:
                f.write("\nФАЙЛЫ С НИЗКИМ БИТРЕЙТОМ (< 192 kbps):\n")
                for item in stats["suspicious"]:
                    f.write(f"  {item['file']} - {item['bitrate']} kbps ({item['size_kb']} KB)\n")
            else:
                f.write("\n✅ Все файлы имеют битрейт 192 kbps или выше!\n")
        
        print(f"\n📁 Полный отчет сохранен: {report_file}")
        
    except ImportError:
        print("⚠️ Библиотека mutagen не установлена. Пропускаем проверку битрейта.")
    except Exception as e:
        print(f"⚠️ Ошибка при проверке битрейта: {e}")
        if debug:
            import traceback
            traceback.print_exc()


def main():
    """Главная функция."""
    parser = argparse.ArgumentParser(
        description="Загрузчик музыки с сервиса Яндекс.Музыка\n"
                    "модификация от DeepSeek, на основе исходников llistochek и melivoro\n"
                    "https://github.com/llistochek/yandex-music-downloader\n"
                    "https://github.com/melivoro/yandex-music-downloader-realflac",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    # Группа общих параметров
    common_group = parser.add_argument_group("Общие параметры")
    common_group.add_argument(
        "--quality",
        metavar="<Качество>",
        default=0,
        type=quality_arg,
        help="Качество трека:\n"
             "0 - Низкое (AAC 64kbps)\n"
             "1 - Оптимальное (AAC 192kbps)\n"
             "2 - Лучшее (FLAC)\n"
             "192 - MP3 192kbps\n"
             "256 - MP3 256kbps\n"
             "320 - MP3 320kbps (максимальное качество)\n"
             "(по умолчанию: %(default)s)",
    )
    common_group.add_argument(
        "--skip-existing", action="store_true", help="Пропускать уже загруженные треки (проверяется только наличие файла, без учета качества)"
    )
    common_group.add_argument(
        "--lyrics-format",
        type=lyrics_format_arg,
        default=core.LyricsFormat.NONE,
        help=show_default("Формат текста песни"),
        choices=core.LyricsFormat,
    )
    common_group.add_argument(
        "--add-lyrics", action="store_true", help=argparse.SUPPRESS
    )
    common_group.add_argument(
        "--embed-cover", action="store_true", help="Встраивать обложку в аудиофайл"
    )
    common_group.add_argument(
        "--cover-resolution",
        default=core.DEFAULT_COVER_RESOLUTION,
        metavar="<Разрешение обложки>",
        type=cover_resolution_arg,
        help=show_default(
            'Разрешение обложки (в пикселях). Передайте "original" для загрузки в оригинальном (наилучшем) разрешении'
        ),
    )
    common_group.add_argument(
        "--delay",
        default=DEFAULT_DELAY,
        metavar="<Задержка>",
        type=checked_int_arg(0),
        help=show_default("Задержка между запросами, в секундах"),
    )
    common_group.add_argument(
        "--stick-to-artist",
        action="store_true",
        help="Загружать альбомы, созданные только данным исполнителем",
    )
    common_group.add_argument(
        "--only-music",
        action="store_true",
        help="Загружать только музыкальные альбомы (пропускать подкасты и аудиокниги)",
    )
    common_group.add_argument(
        "--compatibility-level",
        metavar="<Уровень совместимости>",
        default=1,
        type=checked_int_arg(core.MIN_COMPATIBILITY_LEVEL, core.MAX_COMPATIBILITY_LEVEL),
        help=show_default(
            f"Уровень совместимости, от {core.MIN_COMPATIBILITY_LEVEL} до {core.MAX_COMPATIBILITY_LEVEL}"
        ),
    )
    common_group.add_argument(
        "--save-unavailable",
        action="store_true",
        help="Сохранять список недоступных треков в файл"
    )
    common_group.add_argument(
        "--list-only",
        action="store_true",
        help="Только сохранить список треков в файл (без скачивания).\n"
             "Файл сохраняется в папку --dir с именем tracks_list_YYYYMMDD_HHMMSS.txt"
    )
    common_group.add_argument(
        "--recheck",
        action="store_true",
        help="Проверить реальный битрейт загруженных MP3-файлов после завершения загрузки"
    )
    common_group.add_argument(
        "--debug",
        action="store_true",
        help="Включить режим отладки (вывод подробной информации о работе скрипта)"
    )
    common_group.add_argument(
        "--force-mp3",
        action="store_true",
        help="Принудительно конвертировать AAC в MP3 для качества 0 и 1.\n"
             "Для --quality 0 используется битрейт 64kbps, для --quality 1 - 192kbps.\n"
             "Работает только совместно с --quality 0 или --quality 1."
    )

    # Группа сетевых параметров
    network_group = parser.add_argument_group("Сетевые параметры")
    network_group.add_argument(
        "--timeout",
        metavar="<Время ожидания>",
        default=20,
        type=checked_int_arg(1),
        help=show_default("Время ожидания ответа от сервера, в секундах"),
    )
    network_group.add_argument(
        "--tries",
        metavar="<Количество попыток>",
        default=20,
        type=checked_int_arg(0),
        help=show_default("Количество попыток при возникновении сетевых ошибок. 0 - бесконечно"),
    )
    network_group.add_argument(
        "--retry-delay",
        metavar="<Задержка>",
        default=5,
        type=checked_int_arg(0),
        help=show_default("Задержка между повторными запросами при сетевых ошибках"),
    )

    # Группа ID
    id_group_meta = parser.add_argument_group("ID")
    id_group = id_group_meta.add_mutually_exclusive_group(required=True)
    id_group.add_argument("--artist-id", metavar="<ID исполнителя>")
    id_group.add_argument("--album-id", metavar="<ID альбома>")
    id_group.add_argument("--track-id", metavar="<ID трека>")
    id_group.add_argument(
        "--playlist-id",
        metavar="<владелец плейлиста>/<тип плейлиста>",
    )
    id_group.add_argument("-u", "--url", help="URL исполнителя/альбома/трека/плейлиста")

    # Группа указания пути
    path_group = parser.add_argument_group("Указание пути")
    path_group.add_argument(
        "--unsafe-path",
        action="store_true",
        help="Не очищать путь от недопустимых символов",
    )
    path_group.add_argument(
        "--dir",
        default=".",
        metavar="<Папка>",
        help=show_default("Папка для загрузки музыки"),
        type=Path,
    )
    path_group.add_argument(
        "--path-pattern",
        default=core.DEFAULT_PATH_PATTERN,
        metavar="<Паттерн>",
        type=Path,
        help=show_default(
            "Поддерживает следующие заполнители:"
            " #number, #track-artist, #album-artist, #title,"
            " #album, #year, #artist-id, #album-id, #track-id, #number-padded"
        ),
    )

    # Группа авторизации
    auth_group = parser.add_argument_group("Авторизация")
    auth_group.add_argument(
        "--token",
        required=True,
        metavar="<Токен>",
        help="Токен для авторизации. См. README для способов получения",
    )

    # Добавляем примеры использования
    parser.epilog = """
ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ:

1. Скачать трек в FLAC (максимальное качество):
   yandex-music-downloader --token "ТОКЕН" --quality 2 --url "https://music.yandex.ru/track/6705392"

2. Скачать альбом в MP3 320kbps (высокое качество):
   yandex-music-downloader --token "ТОКЕН" --quality 320 --url "https://music.yandex.ru/album/294912"

3. Скачать все треки исполнителя в MP3 256kbps:
   yandex-music-downloader --token "ТОКЕН" --quality 256 --url "https://music.yandex.ru/artist/208167"

4. Скачать плейлист по ссылке с UUID:
   yandex-music-downloader --token "ТОКЕН" --quality 192 --url "https://music.yandex.ru/playlists/d4f2a00a-b2b1-fc4f-12be-a951f743eb90"

5. Скачать плейлист "Мне нравится":
   yandex-music-downloader --token "ТОКЕН" --quality 320 --url "https://music.yandex.ru/playlists/lk.b083603e-4960-4edb-8640-a82c1f9712dc"

6. Скачать с пропуском уже загруженных файлов и сохранением списка недоступных:
   yandex-music-downloader --token "ТОКЕН" --quality 256 --skip-existing --save-unavailable --url "https://music.yandex.ru/playlists/..."

7. Скачать в режиме отладки (для решения проблем):
   yandex-music-downloader --token "ТОКЕН" --quality 2 --debug --url "https://music.yandex.ru/track/6705392"

8. Сохранить список недоступных треков при скачивании плейлиста:
   yandex-music-downloader --token "ТОКЕН" --quality 320 --save-unavailable --url "https://music.yandex.ru/playlists/d4f2a00a-b2b1-fc4f-12be-a951f743eb90"

9. Принудительная конвертация AAC в MP3 при качестве 0 (64kbps):
   yandex-music-downloader --token "ТОКЕН" --quality 0 --force-mp3 --url "https://music.yandex.ru/album/294912"

10. Принудительная конвертация AAC в MP3 при качестве 1 (192kbps):
    yandex-music-downloader --token "ТОКЕН" --quality 1 --force-mp3 --url "https://music.yandex.ru/album/294912"

11. Проверить реальный битрейт загруженных MP3-файлов:
    yandex-music-downloader --token "ТОКЕН" --quality 320 --recheck --url "https://music.yandex.ru/album/294912"

12. Только сохранить список треков из плейлиста (без скачивания):
    yandex-music-downloader --token "ТОКЕН" --list-only --url "https://music.yandex.ru/playlists/..."
"""

    args = parser.parse_args()

    # Проверка валидности force-mp3
    if args.force_mp3 and args.quality not in (0, 1):
        print("⚠️ Предупреждение: --force-mp3 работает только с --quality 0 или --quality 1")
        print("   Параметр --force-mp3 будет проигнорирован")

    # Настройка логирования
    debug_print(args.debug, f"Аргументы: quality={args.quality}, skip_existing={args.skip_existing}, dir={args.dir}")
    debug_print(args.debug, f"path_pattern={args.path_pattern}, force_mp3={args.force_mp3}, recheck={args.recheck}, list_only={args.list_only}")

    logging.basicConfig(
        format="%(asctime)s |%(levelname)s| %(name)s: %(message)s",
        datefmt="%H:%M:%S",
        level=logging.DEBUG if args.debug else logging.ERROR,
    )

    if args.add_lyrics:
        print("Аргумент --add-lyrics устарел и будет удален в будущем. Используйте --lyrics-format")
        args.lyrics_format = core.LyricsFormat.TEXT

    # Инициализация клиента
    client = core.init_client(
        token=args.token,
        timeout=args.timeout,
        max_try_count=args.tries,
        retry_delay=args.retry_delay,
    )
    client.token = args.token
    
    # Обработка URL
    playlist_id = args.playlist_id
    
    if args.url is not None:
        parsed_url = urlparse(args.url)
        path = parsed_url.path
        
        if match := ARTIST_RE.search(path):
            args.artist_id = match.group(1)
        elif match := ALBUM_RE.search(path):
            args.album_id = match.group(1)
        elif match := TRACK_RE.search(path):
            args.track_id = match.group(1)
        elif match := PLAYLIST_UUID_RE.search(path):
            playlist_uuid = match.group(1)
            print(f"Обнаружен плейлист с UUID: {playlist_uuid}")
            print(f"Получаем информацию о плейлисте...")
            
            playlist_info = get_playlist_info_from_uuid(client, playlist_uuid, args.debug)
            if playlist_info:
                playlist_id = playlist_info
                print(f"✅ Найден плейлист: {playlist_id}")
            else:
                print("❌ Не удалось получить информацию о плейлисте.")
                return 1
        elif match := PLAYLIST_RE.search(path):
            playlist_id = match.group(1) + "/" + match.group(2)
        else:
            print("Параметер url указан в неверном формате")
            return 1
    
    if playlist_id is not None:
        args.playlist_id = playlist_id

    # Получение списка треков
    result_tracks: Iterable[Track] = iter([])
    total_track_count = None

    def album_tracks_gen(album_ids: Iterable[Union[int, str]]) -> Generator[Track]:
        for album_id in album_ids:
            if full_album := client.albums_with_tracks(album_id):
                if volumes := full_album.volumes:
                    yield from itertools.chain.from_iterable(volumes)

    if args.artist_id is not None:
        def filter_album(album: Album) -> bool:
            title = album.title
            if album.id is None or not album.available:
                print(f'Альбом "{title}" не доступен для скачивания')
            elif args.only_music and album.meta_type != "music":
                print(f'Альбом "{title}" пропущен т.к. не является музыкальным')
            elif args.stick_to_artist and album.artists[0].id != int(args.artist_id):
                print(f'Альбом "{title}" пропущен из-за флага --stick-to-artist')
            else:
                return True
            return False

        def albums_id_gen() -> Generator[int]:
            has_next = True
            page = 0
            while has_next:
                if albums_info := client.artists_direct_albums(args.artist_id, page):
                    for album in albums_info.albums:
                        if filter_album(album):
                            assert album.id
                            yield album.id
                        else:
                            nonlocal total_track_count
                            if (track_count := album.track_count) and total_track_count is not None:
                                total_track_count -= track_count
                else:
                    break
                if pager := albums_info.pager:
                    page = pager.page + 1
                    has_next = pager.per_page * page < pager.total
                else:
                    break

        result_tracks = album_tracks_gen(albums_id_gen())
        artist = client.artists(args.artist_id)[0]
        if counts := artist.counts:
            total_track_count = counts.tracks

    elif args.album_id is not None:
        result_tracks = album_tracks_gen((args.album_id,))
        if album := client.albums_with_tracks(args.album_id):
            total_track_count = album.track_count

    elif args.track_id is not None:
        track = client.tracks(args.track_id)
        # Проверяем, не вернулся ли список (например, если ID был передан как строка)
        if isinstance(track, list):
            if track:
                track = track[0]
            else:
                print("Трек не найден")
                return 1
        result_tracks = [track]
        total_track_count = 1

    elif args.playlist_id is not None:
        # Плейлист "Мне нравится"
        if args.playlist_id.startswith('liked/'):
            print(f"  Получаем избранные треки...")
            
            try:
                likes = client.users_likes_tracks()
                
                if likes:
                    track_ids = [track.id for track in likes if hasattr(track, 'id')]
                    
                    if track_ids:
                        print(f"  ✅ Найдено {len(track_ids)} избранных треков")
                        print(f"  Найдено {len(track_ids)} ID треков, получаем данные...")
                        
                        all_tracks = []
                        for i in range(0, len(track_ids), 50):
                            batch = track_ids[i:i+50]
                            try:
                                batch_tracks = client.tracks(batch)
                                if batch_tracks:
                                    all_tracks.extend(batch_tracks)
                            except Exception as e:
                                print(f"  ⚠️ Ошибка при получении батча треков: {e}")
                        
                        all_tracks = [t for t in all_tracks if t is not None]
                        print(f"  Получено {len(all_tracks)} полноценных треков")
                        result_tracks = (track for track in all_tracks)
                        total_track_count = len(all_tracks)
                    else:
                        print(f"  ⚠️ Не найдено ID треков в избранном")
                else:
                    print(f"  ⚠️ Нет избранных треков")
                    
            except Exception as e:
                print(f"  ❌ Ошибка при получении избранных треков: {e}")
                if args.debug:
                    import traceback
                    traceback.print_exc()
                return 1
                
        else:
            # Обычный плейлист
            parts = args.playlist_id.split('/')
            if len(parts) == 2:
                owner, kind = parts[0], parts[1]
                try:
                    print(f"  Получаем плейлист {owner}/{kind}...")
                    playlist = client.users_playlists(kind, owner)
                    if playlist is None:
                        print(f"  ❌ Плейлист {owner}/{kind} не найден")
                        return 1
                    
                    total_track_count = getattr(playlist, 'track_count', 0)
                    print(f"  ✅ Плейлист найден, треков: {total_track_count}")
                    
                    track_ids = []
                    if hasattr(playlist, 'tracks'):
                        for track_item in playlist.tracks:
                            if hasattr(track_item, 'track'):
                                track_obj = track_item.track
                                if hasattr(track_obj, 'id'):
                                    track_ids.append(track_obj.id)
                                elif isinstance(track_obj, dict) and 'id' in track_obj:
                                    track_ids.append(track_obj['id'])
                            elif hasattr(track_item, 'id'):
                                track_ids.append(track_item.id)
                            elif isinstance(track_item, dict) and 'id' in track_item:
                                track_ids.append(track_item['id'])
                    
                    if not track_ids:
                        print(f"  ⚠️ Не найдено ID треков в плейлисте")
                    else:
                        print(f"  Найдено {len(track_ids)} ID треков, получаем данные...")
                        
                        all_tracks = []
                        for i in range(0, len(track_ids), 50):
                            batch = track_ids[i:i+50]
                            try:
                                batch_tracks = client.tracks(batch)
                                if batch_tracks:
                                    all_tracks.extend(batch_tracks)
                            except Exception as e:
                                print(f"  ⚠️ Ошибка при получении батча треков: {e}")
                        
                        all_tracks = [t for t in all_tracks if t is not None]
                        print(f"  Получено {len(all_tracks)} полноценных треков")
                        result_tracks = (track for track in all_tracks)
                        
                except Exception as e:
                    print(f"  ❌ Ошибка при получении плейлиста: {e}")
                    if args.debug:
                        import traceback
                        traceback.print_exc()
                    return 1
            else:
                print(f"  ❌ Неверный формат playlist_id: {args.playlist_id}")
                return 1
    else:
        raise ValueError("Invalid ID argument")

    # ===== НОВЫЙ БЛОК: Если только список =====
    if args.list_only:
        print("\n📋 Режим: только сохранение списка треков (без скачивания)")
        source = args.url or args.playlist_id or "неизвестный источник"
        
        # Сохраняем список
        save_tracks_list(result_tracks, args.dir, source, total_track_count)
        
        # Вывод краткой статистики
        print("\n" + "=" * 60)
        print("📊 СТАТИСТИКА:")
        print(f"  📝 Всего треков в источнике: {total_track_count}")
        print("=" * 60)
        print("\n✅ Список треков сохранен. Для загрузки запустите скрипт без --list-only")
        return 0
    # ===== КОНЕЦ НОВОГО БЛОКА =====

    # Скачивание треков
    track_counter = 0
    progress_status = ""
    covers_cache = {}
    skipped_count = 0
    unavailable_count = 0
    downloaded_count = 0
    error_count = 0
    unavailable_tracks = []

    for track in result_tracks:
        if total_track_count:
            track_counter += 1
            progress_status = f"[{track_counter}/{total_track_count}] "

        # Проверка доступности трека
        if not track.available:
            unavailable_count += 1
            unavailable_tracks.append({
                'id': track.id,
                'title': track.title,
                'artists': get_artists(track),
                'album': track.albums[0].title if track.albums else "Неизвестный альбом"
            })
            print(f"{progress_status}Трек {get_artists(track)} - {track.title} не доступен для скачивания")
            continue

        # Подготовка пути
        base_path = args.dir / core.prepare_base_path(
            args.path_pattern,
            track,
            args.unsafe_path,
            args.debug,
        )
        
        # Проверка существования файла
        if args.skip_existing:
            parent_dir = base_path.parent
            base_name_without_ext = base_path.name
            
            file_found = False
            if parent_dir.exists() and parent_dir.is_dir():
                for existing_file in parent_dir.iterdir():
                    if existing_file.is_file():
                        existing_name_without_ext = existing_file.stem
                        if existing_name_without_ext == base_name_without_ext:
                            file_found = True
                            skipped_count += 1
                            print(f"{progress_status}⚠️ Трек уже загружен (найден {existing_file.name}), пропускаем")
                            break
            
            if file_found:
                continue

        # Создание директории
        save_dir = base_path.parent
        if not save_dir.is_dir():
            save_dir.mkdir(parents=True)

        # Скачивание
        downloadable = core.to_downloadable_track(track, args.quality, base_path, args.debug, args.force_mp3)
        bitrate = downloadable.download_info.bitrate
        format_info = "[" + downloadable.download_info.file_format.codec.name
        if bitrate > 0:
            format_info += f" {bitrate}kbps"
        format_info += "]"
        print(f"{progress_status}{format_info} Загружается {downloadable.path}")
        
        try:
            core.download_track(
                track_info=downloadable,
                lyrics_format=args.lyrics_format,
                embed_cover=args.embed_cover,
                cover_resolution=args.cover_resolution,
                covers_cache=covers_cache,
                compatibility_level=args.compatibility_level,
                debug=args.debug,
                force_mp3=args.force_mp3,
            )
            downloaded_count += 1
        except Exception as e:
            error_count += 1
            print(f"{progress_status}❌ Ошибка при загрузке: {e}")
            if args.debug:
                import traceback
                traceback.print_exc()
        
        if args.delay > 0:
            time.sleep(args.delay)

    # Сохранение списка недоступных треков
    if args.save_unavailable and unavailable_tracks:
        save_unavailable_tracks(unavailable_tracks, args.url or args.playlist_id or "неизвестный источник", args.dir)

    # Вывод статистики
    print("\n" + "=" * 60)
    print("📊 СТАТИСТИКА ЗАГРУЗКИ:")
    print(f"  ✅ Успешно загружено: {downloaded_count}")
    print(f"  ⏭️ Пропущено (уже есть): {skipped_count}")
    print(f"  🚫 Недоступно: {unavailable_count}")
    print(f"  ❌ Ошибок: {error_count}")
    print(f"  📝 Всего треков в плейлисте: {total_track_count}")
    if skipped_count + unavailable_count + error_count > 0:
        print(f"  📊 Итого обработано: {downloaded_count + skipped_count + unavailable_count + error_count}")
    print("=" * 60)
    
    if unavailable_tracks and args.save_unavailable:
        print(f"\n💡 Чтобы проверить недоступные треки позже:")
        print(f"   Найдите файл unavailable_tracks_*.txt в папке {args.dir}")
        print(f"   В нем указаны названия и ID треков")

    # Проверка битрейта, если включен --recheck
    if args.recheck and downloaded_count > 0:
        check_bitrates(args.dir, downloaded_count, args.debug)


if __name__ == "__main__":
    main()