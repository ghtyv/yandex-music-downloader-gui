from PySide6.QtCore import QSettings
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
)

from .generated.ui_settings_dialog import Ui_SettingsDialog


DEFAULT_PATTERN = "#album-artist - #title #track-id"


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui = Ui_SettingsDialog()
        self.ui.setupUi(self)

        ok_button = self.ui.buttonBox.button(
            QDialogButtonBox.StandardButton.Ok
        )

        cancel_button = self.ui.buttonBox.button(
            QDialogButtonBox.StandardButton.Cancel
        )

        ok_button.setText("Сохранить")
        cancel_button.setText("Отмена")

        self.settings = QSettings()

        self.ui.comboBoxCoverMode.clear()
        self.ui.comboBoxCoverMode.addItem(
            "Встраивать в аудиофайл",
            True,
        )
        self.ui.comboBoxCoverMode.addItem(
            "Сохранять отдельным файлом",
            False,
        )

        self.load_settings()

        self.ui.buttonBox.accepted.connect(
            self.save_and_accept
        )
        self.ui.buttonBox.rejected.connect(
            self.reject
        )

    def load_settings(self):
        self.ui.checkBoxSkipExisting.setChecked(
            self.settings.value(
                "download/skip_existing",
                True,
                type=bool,
            )
        )

        embed_cover = self.settings.value(
            "download/embed_cover",
            True,
            type=bool,
        )

        index = self.ui.comboBoxCoverMode.findData(
            embed_cover
        )

        self.ui.comboBoxCoverMode.setCurrentIndex(
            max(index, 0)
        )

        self.ui.spinBoxCoverResolution.setValue(
            self.settings.value(
                "download/cover_resolution",
                400,
                type=int,
            )
        )

        self.ui.lineEditPathPattern.setText(
            self.settings.value(
                "download/path_pattern",
                DEFAULT_PATTERN,
            )
        )

    def save_and_accept(self):
        pattern = (
            self.ui.lineEditPathPattern
            .text()
            .strip()
        )

        if not pattern:
            pattern = DEFAULT_PATTERN

        self.settings.setValue(
            "download/skip_existing",
            self.ui.checkBoxSkipExisting.isChecked(),
        )

        self.settings.setValue(
            "download/embed_cover",
            self.ui.comboBoxCoverMode.currentData(),
        )

        self.settings.setValue(
            "download/cover_resolution",
            self.ui.spinBoxCoverResolution.value(),
        )

        self.settings.setValue(
            "download/path_pattern",
            pattern,
        )

        self.accept()