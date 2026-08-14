import logging
import sys

from PySide6.QtWidgets import QApplication, QMessageBox

from ymd_gui.core.ffmpeg_runtime import (
    check_ffmpeg,
    configure_ffmpeg,
)
from ymd_gui.core.logging_setup import configure_logging
from ymd_gui.gui.generated import resources_rc  # noqa: F401
from ymd_gui.gui.main_window import MainWindow


logger = logging.getLogger(__name__)


def main():
    app = QApplication(sys.argv)

    app.setOrganizationName("YMD GUI")
    app.setApplicationName(
        "Yandex Music Downloader GUI"
    )

    configure_logging()

    ffmpeg_path = configure_ffmpeg()

    if (
        ffmpeg_path is None
        or not check_ffmpeg(ffmpeg_path)
    ):
        logger.error(
            "FFmpeg is missing or cannot be started"
        )

        QMessageBox.critical(
            None,
            "Ошибка FFmpeg",
            (
                "Не удалось запустить FFmpeg.\n\n"
                "Программа не сможет корректно "
                "обрабатывать аудиофайлы."
            ),
        )

        return

    logger.info(
        "FFmpeg initialized: %s",
        ffmpeg_path,
    )

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()