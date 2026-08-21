from pathlib import Path

from keyring.errors import KeyringError

from PySide6.QtGui import QIcon
from PySide6.QtCore import QSettings, QThread, QTimer,  QUrl
from PySide6.QtWidgets import (
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QDialog,
)

from ymd_gui import __version__

from ymd_gui.core.downloader import (
    DEFAULT_PARALLEL_DOWNLOADS,
    MAX_PARALLEL_DOWNLOADS,
    MIN_PARALLEL_DOWNLOADS,
    DownloadConfig,
)
from ymd_gui.core.worker import DownloadWorker

from ymd_gui.core.token_store import (
    delete_token,
    load_token,
    save_token,
)

from ymd_gui.core.temp_cleanup import cleanup_temp_files

from ymd_gui.gui.oauth_dialog import OAuthDialog
from ymd_gui.gui.settings_dialog import (
    DEFAULT_PATTERN,
    SettingsDialog,
)

from .generated.ui_main_window import Ui_MainWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.setWindowIcon(QIcon(":/icons/app.ico"))
        self.ui.setupUi(self)

        self.statusBar().showMessage("Готово")

        self.download_thread = None
        self.download_worker = None

        self.restart_after_auth = False

        self.settings = QSettings()

        self.setup_quality()
        self.load_settings()

        self.active_output_dir = None

        # Выбор папки
        self.ui.pushButtonFolder.clicked.connect(self.select_folder)

        self.ui.pushButtonAuthorization.clicked.connect(
            self.open_oauth
        )

        self.update_auth_state()

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

        # Отмена загрузки
        self.ui.pushButtonCancel.clicked.connect(
            self.cancel_download
        )

        # Настройки
        self.ui.pushButtonSettings.clicked.connect(
            self.open_settings
        )

        # Справка "О программе"
        self.ui.actionAbout.triggered.connect(
            self.show_about
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

    def append_download_log(self, message):
        self.ui.plainTextEditLog.appendPlainText(
            message
        )

    def update_download_progress(
            self,
            current,
            total,
    ):
        if total <= 0:
            return

        progress_bar = self.ui.progressBarDownload

        progress_bar.setRange(0, total)
        progress_bar.setValue(current)
        progress_bar.setFormat(
            "%v / %m (%p%)"
        )

    def download_finished(self, stats):
        progress_bar = self.ui.progressBarDownload

        if stats.total > 0:
            progress_bar.setRange(
                0,
                stats.total,
            )
            progress_bar.setValue(
                stats.total,
            )
            progress_bar.setFormat(
                "%v / %m — готово"
            )
        else:
            progress_bar.setRange(0, 1)
            progress_bar.setValue(1)
            progress_bar.setFormat(
                "Готово"
            )

        self.ui.plainTextEditLog.appendPlainText(
            ""
        )

        self.ui.plainTextEditLog.appendPlainText(
            "=== Завершено ==="
        )

        self.ui.plainTextEditLog.appendPlainText(
            f"Скачано: {stats.downloaded}"
        )
        self.ui.plainTextEditLog.appendPlainText(
            f"Пропущено: {stats.skipped}"
        )
        self.ui.plainTextEditLog.appendPlainText(
            f"Недоступно: {stats.unavailable}"
        )
        self.ui.plainTextEditLog.appendPlainText(
            f"Ошибок: {stats.errors}"
        )

        self.statusBar().showMessage(
            f"Готово — скачано: {stats.downloaded}, "
            f"пропущено: {stats.skipped}"
        )

    def download_failed(
        self,
        error: str,
    ):
        self.ui.progressBarDownload.setRange(
            0,
            1,
        )
        self.ui.progressBarDownload.setValue(0)
        self.ui.progressBarDownload.setFormat(
            "Ошибка"
        )

        self.statusBar().showMessage(
            "Ошибка загрузки"
        )

        self.ui.plainTextEditLog.appendPlainText(
            ""
        )

        self.ui.plainTextEditLog.appendPlainText(
            f"Ошибка: {error}"
        )

        QMessageBox.critical(
            self,
            "Ошибка загрузки",
            error,
        )

    def download_thread_finished(self):
        self.set_download_running(False)

        output_dir = self.active_output_dir

        self.download_worker = None
        self.download_thread = None
        self.active_output_dir = None

        if output_dir is not None:
            removed_tmp = cleanup_temp_files(
                output_dir
            )

            if removed_tmp:
                self.ui.plainTextEditLog.appendPlainText(
                    f"Удалено временных файлов: {removed_tmp}"
                )

        if self.restart_after_auth:
            QTimer.singleShot(
                0,
                self.open_oauth,
            )

    def set_download_running(self, running):
        self.ui.lineEditURL.setEnabled(
            not running
        )
        self.ui.lineEditFolder.setEnabled(
            not running
        )
        self.ui.pushButtonFolder.setEnabled(
            not running
        )
        self.ui.comboBoxQuality.setEnabled(
            not running
        )
        self.ui.pushButtonAuthorization.setEnabled(
            not running
        )

        self.ui.pushButtonDownload.setEnabled(
            not running
        )

        if running:
            self.ui.pushButtonDownload.setText(
                "Скачивание..."
            )
        else:
            self.ui.pushButtonDownload.setText(
                "Скачать"
            )

        self.ui.pushButtonCancel.setEnabled(
            running
        )

        if not running:
            self.ui.pushButtonCancel.setText(
                "Отмена"
            )

    def start_download(self):
        # Защита от двойного запуска
        if (
                self.download_thread is not None
                and self.download_thread.isRunning()
        ):
            return

        valid, error = self.validate_inputs()

        if not valid:
            self.ui.plainTextEditLog.appendPlainText(
                f"Ошибка: {error}"
            )

            QMessageBox.warning(
                self,
                "Некорректные параметры",
                error,
            )

            return

        token = self.get_auth_token()

        if not token:
            return

        quality = self.ui.comboBoxQuality.currentData()

        if quality is None:
            QMessageBox.warning(
                self,
                "Ошибка",
                "Не выбрано качество загрузки.",
            )
            return

        settings = QSettings()

        skip_existing = bool(
            settings.value(
                "download/skip_existing",
                True,
                type=bool,
            )
        )

        embed_cover = bool(
            settings.value(
                "download/embed_cover",
                True,
                type=bool,
            )
        )

        cover_resolution = int(
            settings.value(
                "download/cover_resolution",
                400,
                type=int,
            )
        )

        pattern = str(
            settings.value(
                "download/path_pattern",
                DEFAULT_PATTERN,
                type=str,
            )
        )

        parallel_downloads = max(
            MIN_PARALLEL_DOWNLOADS,
            min(
                MAX_PARALLEL_DOWNLOADS,
                int(
                    settings.value(
                        "download/parallel_downloads",
                        DEFAULT_PARALLEL_DOWNLOADS,
                        type=int,
                    )
                ),
            ),
        )

        config = DownloadConfig(
            token=token,
            url=self.ui.lineEditURL.text().strip(),
            output_dir=Path(
                self.ui.lineEditFolder.text().strip()
            ),
            quality=int(quality),

            skip_existing=skip_existing,
            embed_cover=embed_cover,
            cover_resolution=cover_resolution,
            path_pattern=Path(pattern),
            parallel_downloads=parallel_downloads,

            debug=False
        )

        self.ui.plainTextEditLog.appendPlainText(
            ""
        )
        self.ui.plainTextEditLog.appendPlainText(
            "=== Новая загрузка ==="
        )
        self.ui.plainTextEditLog.appendPlainText(
            f"Ссылка: {config.url}"
        )
        self.ui.plainTextEditLog.appendPlainText(
            f"Папка: {config.output_dir}"
        )
        self.ui.plainTextEditLog.appendPlainText(
            f"Качество: "
            f"{self.ui.comboBoxQuality.currentText()}"
        )

        # Пока список треков ещё неизвестен —
        # progress bar работает в неопределённом режиме.
        self.ui.progressBarDownload.setRange(0, 0)
        self.ui.progressBarDownload.setFormat(
            "Подготовка..."
        )

        removed_tmp = cleanup_temp_files(
            config.output_dir
        )

        if removed_tmp:
            self.ui.plainTextEditLog.appendPlainText(
                f"Удалено временных файлов: {removed_tmp}"
            )

        self.active_output_dir = config.output_dir

        self.set_download_running(True)

        thread = QThread(self)
        worker = DownloadWorker(config)

        worker.moveToThread(thread)

        self.download_thread = thread
        self.download_worker = worker

        # Запуск backend после старта потока
        thread.started.connect(worker.run)

        # Worker -> GUI
        worker.log.connect(self.append_download_log)
        worker.progress.connect(
            self.update_download_progress
        )
        worker.finished.connect(
            self.download_finished
        )
        worker.failed.connect(
            self.download_failed
        )
        worker.auth_required.connect(
            self.download_auth_required
        )
        worker.cancelled.connect(
            self.download_cancelled
        )
        worker.status.connect(
            self.update_download_status
        )

        # Завершаем QThread после завершения worker
        worker.finished.connect(thread.quit)
        worker.failed.connect(thread.quit)
        worker.auth_required.connect(thread.quit)
        worker.cancelled.connect(thread.quit)

        # Корректное уничтожение объектов
        thread.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(
            self.download_thread_finished
        )

        thread.start()

    def closeEvent(self, event):
        if (
                self.download_thread is not None
                and self.download_thread.isRunning()
        ):
            QMessageBox.information(
                self,
                "Загрузка выполняется",
                "Дождитесь окончания загрузки "
                "перед закрытием программы.",
            )

            event.ignore()
            return

        super().closeEvent(event)

    def open_oauth(self):
        dialog = OAuthDialog(self)
        self.setWindowIcon(QIcon(":/icons/app.ico"))

        dialog.token_received.connect(
            self.oauth_token_received
        )

        result = dialog.exec()

        if (
                result != QDialog.DialogCode.Accepted
                and self.restart_after_auth
        ):
            self.restart_after_auth = False

            self.ui.plainTextEditLog.appendPlainText(
                "Повторная авторизация отменена."
            )

    def oauth_token_received(self, token: str):
        try:
            save_token(token)

        except (KeyringError, ValueError) as error:
            QMessageBox.critical(
                self,
                "Ошибка сохранения токена",
                (
                    "Авторизация прошла успешно, "
                    "но сохранить токен не удалось.\n\n"
                    f"{error}"
                ),
            )

            self.ui.plainTextEditLog.appendPlainText(
                "Ошибка: не удалось сохранить OAuth-токен."
            )

            return

        self.update_auth_state()

        self.ui.plainTextEditLog.appendPlainText(
            "Авторизация Яндекс выполнена."
        )

        should_restart = self.restart_after_auth
        self.restart_after_auth = False

        if should_restart:
            self.ui.plainTextEditLog.appendPlainText(
                "Возобновление загрузки..."
            )

            QTimer.singleShot(
                0,
                self.start_download,
            )
        else:
            QMessageBox.information(
                self,
                "Авторизация",
                "Токен Яндекс Музыки успешно получен.",
            )

    def update_auth_state(self):
        try:
            token = load_token()
        except KeyringError:
            token = None

        if token:
            self.ui.pushButtonAuthorization.setText(
                "Обновить токен"
            )

            self.ui.pushButtonAuthorization.setToolTip(
                "OAuth-токен сохранён. "
                "Нажмите для повторной авторизации."
            )

        else:
            self.ui.pushButtonAuthorization.setText(
                "Получить токен"
            )

            self.ui.pushButtonAuthorization.setToolTip(
                "Авторизоваться через Яндекс OAuth"
            )

    def get_auth_token(self) -> str | None:
        try:
            token = load_token()
        except KeyringError as error:
            QMessageBox.critical(
                self,
                "Ошибка хранилища",
                (
                    "Не удалось прочитать сохранённый "
                    "OAuth-токен.\n\n"
                    f"{error}"
                ),
            )
            return None

        if token:
            return token

        QMessageBox.warning(
            self,
            "Требуется авторизация",
            (
                "Сначала получите OAuth-токен "
                "через кнопку «Получить токен»."
            ),
        )

        return None

    def download_auth_required(self):
        self.ui.plainTextEditLog.appendPlainText("")
        self.ui.plainTextEditLog.appendPlainText(
            "OAuth-токен больше не действителен."
        )
        self.ui.plainTextEditLog.appendPlainText(
            "Требуется повторная авторизация..."
        )
        self.statusBar().showMessage(
            "Требуется повторная авторизация"
        )

        delete_token()

        self.update_auth_state()

        self.restart_after_auth = True

    def cancel_download(self):
        if (
                self.download_thread is None
                or not self.download_thread.isRunning()
        ):
            return

        self.ui.pushButtonCancel.setEnabled(False)
        self.ui.pushButtonCancel.setText(
            "Остановка..."
        )

        self.ui.plainTextEditLog.appendPlainText(
            "Запрошена остановка загрузки..."
        )

        self.download_thread.requestInterruption()

    def download_cancelled(self):
        self.ui.progressBarDownload.setFormat(
            "Отменено"
        )

        self.statusBar().showMessage(
            "Загрузка отменена"
        )

        self.ui.plainTextEditLog.appendPlainText(
            "Загрузка остановлена пользователем."
        )

    def open_settings(self):
        SettingsDialog(self).exec()
        self.setWindowIcon(QIcon(":/icons/app.ico"))

    def update_download_status(self, message: str):
        self.statusBar().showMessage(message)

    def show_about(self):
        QMessageBox.about(
            self,
            "О программе",
            (
                "<h2>Yandex Music Downloader GUI</h2>"
                f"<p>Версия {__version__}</p>"
                "<p>"
                "Графическое приложение для загрузки музыки "
                "из Яндекс Музыки."
                "</p>"
                "<p>"
                "Backend основан на проекте "
                "<b>llistochek/yandex-music-downloader</b> "
                "и дополнительных модификациях."
                "</p>"
                "<p>"
                "Для обработки аудио используется FFmpeg."
                "</p>"
                "<p>"
                "<b>Независимый проект, не связанный "
                "с компанией Яндекс.</b>"
                "</p>"
            ),
        )
