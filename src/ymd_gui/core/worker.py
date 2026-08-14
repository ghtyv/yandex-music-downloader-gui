from __future__ import annotations

import traceback

from PySide6.QtCore import QObject, Signal, Slot

from ymd_gui.core.downloader import (
    DownloadConfig,
    Downloader,
)

from yandex_music.exceptions import UnauthorizedError


class DownloadWorker(QObject):
    log = Signal(str)
    auth_required = Signal()

    # current, total
    progress = Signal(int, int)

    # DownloadStats
    finished = Signal(object)

    # короткое сообщение, полный traceback
    failed = Signal(str, str)

    def __init__(self, config: DownloadConfig):
        super().__init__()
        self.config = config

    @Slot()
    def run(self):
        try:
            downloader = Downloader(
                log_callback=self.log.emit,
                progress_callback=self.progress.emit,
            )

            stats = downloader.download(self.config)

        except UnauthorizedError:
            self.auth_required.emit()
            return

        except Exception as error:
            self.failed.emit(
                str(error),
                traceback.format_exc(),
            )
            return

        self.finished.emit(stats)