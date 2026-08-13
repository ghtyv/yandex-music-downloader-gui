from pathlib import Path

from PySide6.QtCore import QSettings, QUrl
from PySide6.QtWidgets import (
    QFileDialog,
    QMainWindow,
    QMessageBox,
)

from .generated.ui_main_window import Ui_MainWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.settings = QSettings()

        self.setup_quality()
        self.load_settings()

        # Выбор папки
        self.ui.pushButtonFolder.clicked.connect(self.select_folder)

        # Ручное изменение пути
        self.ui.lineEditFolder.editingFinished.connect(
            self.save_folder_from_input
        )

        # Качество
        self.ui.comboBoxQuality.currentIndexChanged.connect(
            self.save_quality
        )

        # Скачать
        self.ui.pushButtonDownload.clicked.connect(
            self.start_download
        )

    def setup_quality(self):
        self.ui.comboBoxQuality.clear()

        self.ui.comboBoxQuality.addItem(
            "Лучшее доступное (FLAC / MP3)", 2
        )
        self.ui.comboBoxQuality.addItem(
            "MP3 320 kbps", 320
        )
        self.ui.comboBoxQuality.addItem(
            "MP3 256 kbps", 256
        )
        self.ui.comboBoxQuality.addItem(
            "MP3 192 kbps", 192
        )
        self.ui.comboBoxQuality.addItem(
            "AAC 192 kbps", 1
        )
        self.ui.comboBoxQuality.addItem(
            "AAC 64 kbps", 0
        )

    def load_settings(self):
        folder = self.settings.value(
            "download/folder",
            ""
        )

        quality = self.settings.value(
            "download/quality",
            2,
            type=int
        )

        self.ui.lineEditFolder.setText(folder)

        index = self.ui.comboBoxQuality.findData(quality)

        if index >= 0:
            self.ui.comboBoxQuality.setCurrentIndex(index)
        else:
            self.ui.comboBoxQuality.setCurrentIndex(0)

    def select_folder(self):
        current_folder = self.ui.lineEditFolder.text().strip()

        folder = QFileDialog.getExistingDirectory(
            self,
            "Выберите папку для сохранения",
            current_folder
        )

        if folder:
            self.ui.lineEditFolder.setText(folder)
            self.save_folder(folder)

    def save_folder_from_input(self):
        folder = self.ui.lineEditFolder.text().strip()

        # Убираем случайные пробелы по краям
        self.ui.lineEditFolder.setText(folder)

        self.save_folder(folder)

    def save_folder(self, folder):
        self.settings.setValue(
            "download/folder",
            folder
        )

    def save_quality(self):
        quality = self.ui.comboBoxQuality.currentData()

        self.settings.setValue(
            "download/quality",
            quality
        )

    def validate_url(self):
        url_text = self.ui.lineEditURL.text().strip()

        if not url_text:
            return False, "Введите ссылку на Яндекс Музыку."

        url = QUrl(url_text)

        if not url.isValid():
            return False, "Введена некорректная ссылка."

        if url.scheme().lower() not in ("http", "https"):
            return False, "Ссылка должна начинаться с http:// или https://."

        host = url.host().lower()

        if host not in (
            "music.yandex.ru",
            "www.music.yandex.ru",
        ):
            return False, "Введите ссылку именно на Яндекс Музыку."

        return True, ""

    def validate_folder(self):
        folder_text = self.ui.lineEditFolder.text().strip()

        if not folder_text:
            return False, "Выберите папку для сохранения музыки."

        folder = Path(folder_text)

        if not folder.exists():
            return False, "Указанная папка не существует."

        if not folder.is_dir():
            return False, "Указанный путь не является папкой."

        return True, ""

    def validate_inputs(self):
        url_valid, url_error = self.validate_url()

        if not url_valid:
            self.ui.lineEditURL.setFocus()
            return False, url_error

        folder_valid, folder_error = self.validate_folder()

        if not folder_valid:
            self.ui.lineEditFolder.setFocus()
            return False, folder_error

        return True, ""

    def start_download(self):
        valid, error = self.validate_inputs()

        if not valid:
            self.ui.plainTextEditLog.appendPlainText(
                f"Ошибка: {error}"
            )

            QMessageBox.warning(
                self,
                "Некорректные параметры",
                error
            )

            return

        url = self.ui.lineEditURL.text().strip()
        folder = self.ui.lineEditFolder.text().strip()
        quality_name = self.ui.comboBoxQuality.currentText()
        quality = self.ui.comboBoxQuality.currentData()

        self.ui.plainTextEditLog.appendPlainText(
            "Параметры проверены."
        )
        self.ui.plainTextEditLog.appendPlainText(
            f"Ссылка: {url}"
        )
        self.ui.plainTextEditLog.appendPlainText(
            f"Папка: {folder}"
        )
        self.ui.plainTextEditLog.appendPlainText(
            f"Качество: {quality_name} ({quality})"
        )
        self.ui.plainTextEditLog.appendPlainText(
            "Загрузчик пока не подключён."
        )