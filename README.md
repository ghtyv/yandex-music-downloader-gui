# Yandex Music Downloader GUI

Графическое приложение для загрузки музыки из Яндекс Музыки.

Проект основан на [yandex-music-downloader](https://github.com/llistochek/yandex-music-downloader) с дополнительными изменениями backend и собственным интерфейсом на PySide6.

> [!IMPORTANT]
> Это независимый проект, не связанный с компанией Яндекс.

## Возможности

- графический интерфейс для Windows;
- встроенная OAuth-авторизация Яндекс;
- получение OAuth-токена через встроенное окно авторизации;
- хранение OAuth-токена в системном хранилище учётных данных;
- загрузка отдельных треков, альбомов и плейлистов;
- поддержка UUID-ссылок на плейлисты;
- загрузка в лучшем доступном качестве;
- поддержка FLAC;
- автоматический fallback, если lossless для трека недоступен;
- обработка и преобразование аудио через FFmpeg;
- встраивание обложек;
- сохранение обложек отдельными файлами;
- настройка разрешения обложки;
- пропуск уже скачанных треков;
- пользовательский шаблон имени и пути файлов;
- отображение прогресса и текущего состояния загрузки;
- безопасная остановка загрузки;
- повторная OAuth-авторизация при недействительном токене;
- продолжение большой загрузки после повторной авторизации с пропуском уже скачанных файлов;
- автоматическая очистка оставшихся временных файлов;
- пользовательский журнал и отдельный технический debug-лог;
- bundled FFmpeg в Windows-сборке;
- Portable-сборка без необходимости отдельно устанавливать Python или FFmpeg.

## Windows

Поддерживаются:

- Windows 10 x64;
- Windows 11 x64.

Готовая Portable-сборка находится в разделе **Releases**.

### Установка

Установка не требуется.

1. Скачайте архив:

```text
YandexMusicDownloader-<version>-Windows-x64.zip
```

2. Распакуйте его в любую папку.

3. Запустите:

```text
YandexMusicDownloader.exe
```

Python и FFmpeg отдельно устанавливать не требуется.

## Использование

1. Запустите приложение.
2. Нажмите **«Получить токен»**.
3. Авторизуйтесь в Яндекс через встроенное окно.
4. Вставьте ссылку на трек, альбом или плейлист.
5. Выберите папку для сохранения.
6. Выберите качество.
7. При необходимости измените дополнительные параметры через **«Настройки»**.
8. Нажмите **«Скачать»**.

Во время загрузки приложение отображает текущий статус, прогресс и журнал операций.

Загрузку можно безопасно остановить кнопкой **«Отмена»**.

## Качество

Режим:

```text
Лучшее доступное (FLAC / MP3)
```

пытается получить максимально доступное качество.

Если трек доступен в lossless, он сохраняется в FLAC.

Если lossless недоступен, приложение использует доступный аудиопоток и при необходимости преобразует его в MP3.

Для обработки контейнеров и преобразования аудио используется FFmpeg.

## Настройки

Доступны:

- пропуск уже скачанных треков;
- встраивание обложки в аудиофайл;
- сохранение обложки отдельно;
- настройка разрешения обложки;
- пользовательский шаблон имени и пути файлов.

Стандартный шаблон:

```text
#album-artist - #title #track-id
```

Поддерживаются заполнители, включая:

```text
#number
#number-padded
#track-artist
#album-artist
#title
#album
#year
#artist-id
#album-id
#track-id
```

Шаблоны могут использоваться и для создания структуры каталогов.

Например:

```text
#track-artist/#album/#number-padded - #title
```

может создать:

```text
Исполнитель/
└── Альбом/
    ├── 01 - Первый трек.flac
    ├── 02 - Второй трек.flac
    └── ...
```

## Авторизация

OAuth-авторизация выполняется во встроенном окне приложения.

Полученный OAuth-токен не записывается в исходный код или обычный конфигурационный файл приложения.

Для хранения токена используется системное хранилище учётных данных.

> [!WARNING]
> Не публикуйте и не передавайте свой OAuth-токен другим людям.

Если во время длительной загрузки токен становится недействительным, приложение предлагает пройти OAuth-авторизацию повторно.

После получения нового токена загрузка может быть продолжена, а уже скачанные файлы — пропущены.

## FFmpeg

Для обработки аудио используется [FFmpeg](https://ffmpeg.org/).

Windows Portable-сборка использует LGPL shared build от [BtbN/FFmpeg-Builds](https://github.com/BtbN/FFmpeg-Builds).

Текущая bundled-сборка:

```text
Provider: BtbN / FFmpeg-Builds
Variant: win64-lgpl-shared-8.1
FFmpeg: n8.1.2-40-g852b0552f0-20260814
FFmpeg commit: 852b0552f0
BtbN FFmpeg-Builds commit: 590a6612d7d961e9258429e501619e0b7d7cbedf
BtbN release: autobuild-2026-08-14-13-16
License: LGPLv3
```

FFmpeg и необходимые DLL уже включены в Windows Portable-сборку, поэтому пользователю не требуется устанавливать FFmpeg отдельно.

Для релиза также предоставляется соответствующий source bundle:

```text
FFmpeg-BtbN-20260814-Sources.zip
```

Он содержит:

- исходный код FFmpeg для используемой revision;
- BtbN FFmpeg-Builds scripts;
- patches и build configuration;
- исходные архивы внешних зависимостей;
- license files;
- информацию о конкретной используемой сборке;
- SHA-256 manifest.

Дополнительная информация находится в:

```text
THIRD_PARTY_NOTICES.txt
LICENSES/
```

## Сборка из исходников

Для разработки используется Python 3.13.

### Создание виртуального окружения

```powershell
py -3.13 -m venv .venv
```

### Установка проекта

```powershell
.\.venv\Scripts\python.exe -m pip install -e .
```

### Запуск

```powershell
.\.venv\Scripts\python.exe -m ymd_gui.main
```

## FFmpeg для разработки

Bundled FFmpeg для локальной Windows-разработки находится в:

```text
src/ymd_gui/resources/ffmpeg/windows/
```

Для BtbN shared build в этой папке находятся:

```text
ffmpeg.exe
*.dll
```

Сами FFmpeg binaries и DLL не хранятся в Git-репозитории.

Если bundled FFmpeg отсутствует, приложение может использовать системный FFmpeg, доступный через `PATH`.

## Qt Designer

Формы интерфейса находятся в:

```text
src/ymd_gui/gui/forms/
```

После изменения `.ui` необходимо заново сгенерировать соответствующий Python-файл с помощью `pyside6-uic`.

Например:

```powershell
.\.venv\Scripts\pyside6-uic.exe `
  .\src\ymd_gui\gui\forms\main_window.ui `
  -o .\src\ymd_gui\gui\generated\ui_main_window.py
```

## Qt Resources

Ресурсы Qt описаны в:

```text
src/ymd_gui/resources/resources.qrc
```

После изменения `.qrc` необходимо заново создать:

```text
src/ymd_gui/gui/generated/resources_rc.py
```

Команда:

```powershell
.\.venv\Scripts\pyside6-rcc.exe `
  .\src\ymd_gui\resources\resources.qrc `
  -o .\src\ymd_gui\gui\generated\resources_rc.py
```

## Windows build

Для создания Portable Windows-сборки используется Nuitka.

Установите зависимости сборки:

```powershell
.\.venv\Scripts\python.exe -m pip install nuitka ordered-set zstandard
```

Сборка standalone-приложения и создание Portable ZIP выполняются одной командой:

```powershell
.\scripts\build_windows.ps1
```

Готовый архив создаётся в:

```text
dist/
```

Например:

```text
YandexMusicDownloader-0.1.0-Windows-x64.zip
```

## FFmpeg source bundle

Source bundle для bundled FFmpeg формируется отдельным GitHub Actions workflow:

```text
.github/workflows/build_ffmpeg_source_bundle.yml
```

Workflow создаёт:

```text
FFmpeg-BtbN-20260814-Sources.zip
```

Этот архив публикуется в том же Release, что и Windows Portable-сборка.

## Структура проекта

```text
yandex-music-downloader-gui/
├── .github/
│   └── workflows/
│       └── build_ffmpeg_source_bundle.yml
│
├── assets/
│   └── icon.png
│
├── packaging/
│   └── windows/
│       ├── LICENSES/
│       ├── README.txt
│       └── THIRD_PARTY_NOTICES.txt
│
├── scripts/
│   └── build_windows.ps1
│
├── third_party_sources/
│   └── ffmpeg/
│       └── SOURCE_INFO.txt
│
├── src/
│   ├── ymd/
│   │   └── backend yandex-music-downloader
│   │
│   └── ymd_gui/
│       ├── core/
│       │   ├── downloader.py
│       │   ├── worker.py
│       │   ├── token_store.py
│       │   ├── ffmpeg_runtime.py
│       │   ├── logging_setup.py
│       │   └── temp_cleanup.py
│       │
│       ├── gui/
│       │   ├── forms/
│       │   ├── generated/
│       │   ├── widgets/
│       │   ├── main_window.py
│       │   ├── settings_dialog.py
│       │   └── oauth_dialog.py
│       │
│       ├── resources/
│       ├── __init__.py
│       └── main.py
│
├── .gitignore
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Сторонние проекты

Проект использует сторонние open-source компоненты, включая:

- [llistochek/yandex-music-downloader](https://github.com/llistochek/yandex-music-downloader)
- [FFmpeg](https://ffmpeg.org/)
- [BtbN/FFmpeg-Builds](https://github.com/BtbN/FFmpeg-Builds)
- Qt
- PySide6
- [MarshalX/yandex-music-api](https://github.com/MarshalX/yandex-music-api) (`yandex-music`) — неофициальная Python-библиотека для работы с API Яндекс Музыки
- Nuitka

Информация о лицензиях компонентов, включённых в готовую Windows-сборку, находится в:

```text
THIRD_PARTY_NOTICES.txt
LICENSES/
```

## Логи

Приложение ведёт отдельный технический debug-лог.

Технические traceback не выводятся в пользовательский журнал интерфейса.

OAuth-токен в debug-лог не записывается.

## Дисклеймер

Yandex Music Downloader GUI является независимым проектом и не связан с компанией Яндекс.

Программа предоставляется как инструмент для работы с доступным пользователю контентом.

Пользователь самостоятельно несёт ответственность за соблюдение условий использования соответствующих сервисов и применимого законодательства.