import sys

from PySide6.QtWidgets import QApplication

from ymd_gui.gui.main_window import MainWindow

from ymd_gui.gui.generated import resources_rc  # noqa: F401

from ymd_gui.core.ffmpeg_runtime import (
    configure_ffmpeg,
)


def main():
    app = QApplication(sys.argv)

    app.setOrganizationName("YMD GUI")
    app.setApplicationName("Yandex Music Downloader GUI")

    ffmpeg_path = configure_ffmpeg()

    if ffmpeg_path is None:
        print("FFmpeg not found")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()