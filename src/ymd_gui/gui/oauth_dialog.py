from urllib.parse import parse_qs

from PySide6.QtCore import QUrl, Signal
from PySide6.QtWebEngineCore import (
    QWebEnginePage,
    QWebEngineProfile,
)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QProgressBar,
    QSizePolicy,
    QVBoxLayout,
)


OAUTH_URL = (
    "https://oauth.yandex.ru/authorize"
    "?response_type=token"
    "&client_id=23cabbbdc6cd418abb4b39c32c41195d"
)


class OAuthDialog(QDialog):
    token_received = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Авторизация Яндекс")
        self.resize(950, 720)

        self.status_label = QLabel(
            "Войдите в аккаунт Яндекса и разрешите доступ."
        )

        self.status_label.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Fixed,
        )
        self.status_label.setMaximumHeight(32)

        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("oauthProgressBar")
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(4)

        self.web_view = QWebEngineView(self)
        self.web_view.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self.status_label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.web_view)

        layout.setStretch(0, 0)
        layout.setStretch(1, 0)
        layout.setStretch(2, 1)

        # Отдельный приватный профиль.
        # Cookies/cache этого окна не сохраняются на диск.
        self.profile = QWebEngineProfile(self)

        self.page = QWebEnginePage(
            self.profile,
            self.web_view,
        )

        self.web_view.setPage(self.page)

        self.web_view.urlChanged.connect(
            self._check_url
        )

        self.web_view.loadProgress.connect(
            self.progress_bar.setValue
        )

        self.web_view.loadFinished.connect(
            self._load_finished
        )

        self.web_view.setUrl(
            QUrl(OAUTH_URL)
        )

    def _load_finished(self, ok: bool):
        if ok:
            self.status_label.setText(
                "Ожидание авторизации..."
            )
        else:
            self.status_label.setText(
                "Не удалось загрузить страницу."
            )

    def _check_url(self, url: QUrl):
        # Нас интересует именно конечный redirect
        # на music.yandex.ru.
        if url.host().lower() != "music.yandex.ru":
            return

        fragment = url.fragment()

        if not fragment:
            return

        params = parse_qs(fragment)

        token_values = params.get("access_token")

        if token_values:
            token = token_values[0].strip()

            if not token:
                return

            # Останавливаем страницу до дальнейшей обработки URL.
            self.web_view.stop()

            self.status_label.setText(
                "Авторизация выполнена."
            )

            self.token_received.emit(token)

            # Не оставляем страницу с токеном открытой.
            self.web_view.setUrl(
                QUrl("about:blank")
            )

            self.accept()
            return

        error_values = params.get("error")

        if error_values:
            error = error_values[0]

            self.status_label.setText(
                f"Ошибка OAuth: {error}"
            )