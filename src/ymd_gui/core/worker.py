from __future__ import annotations

import logging

from PySide6.QtCore import QObject, QThread, Signal, Slot

from ymd_gui.core.downloader import (
    DownloadCancelled,
    DownloadConfig,
    Downloader,
)

from yandex_music.exceptions import UnauthorizedError

logger = logging.getLogger(__name__)


class DownloadWorker(QObject):
    log = Signal(str)
    auth_required = Signal()
    cancelled = Signal()
    status = Signal(str)

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
                status_callback=self.status.emit,
                cancel_callback=lambda: (
                    QThread.currentThread()
                    .isInterruptionRequested()
                ),
            )

            stats = downloader.download(
                self.config
            )

        except DownloadCancelled:
            logger.info(
                "Download cancelled by user"
            )

            self.cancelled.emit()
            return

        except UnauthorizedError:
            logger.warning(
                "OAuth token rejected during download"
            )

            self.auth_required.emit()
            return

        except Exception:
            # Полный traceback автоматически идёт
            # только в debug.log.
            logger.exception(
                "Unhandled download worker error"
            )

            self.failed.emit(
                "Не удалось завершить загрузку."
            )

            return

        self.finished.emit(stats)