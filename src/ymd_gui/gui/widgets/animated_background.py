import math

from PySide6.QtCore import QElapsedTimer, QTimer
from PySide6.QtGui import QColor, QPainter, QRadialGradient, QBrush
from PySide6.QtWidgets import QWidget


class AnimatedBackground(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._clock = QElapsedTimer()
        self._clock.start()

        self._timer = QTimer(self)
        self._timer.setInterval(16)  # ~60 FPS
        self._timer.timeout.connect(self.update)
        self._timer.start()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()

        # Более тёмная база
        painter.fillRect(
            self.rect(),
            QColor("#070707"),
        )

        t = self._clock.elapsed() / 1000.0

        blobs = [
            # Основное жёлтое ядро — заметное, но не на весь экран
            (
                0.42 + 0.04 * math.sin(t * 0.14),
                0.50 + 0.03 * math.cos(t * 0.13),
                0.82,
                QColor(255, 208, 20, 88),
            ),

            # Второй золотой слой для глубины
            (
                0.57 + 0.03 * math.cos(t * 0.12),
                0.57 + 0.03 * math.sin(t * 0.13),
                0.62,
                QColor(255, 184, 0, 52),
            ),

            # Небольшой тёплый оранжевый снизу
            (
                0.34 + 0.04 * math.sin(t * 0.11),
                0.82 + 0.03 * math.cos(t * 0.12),
                0.48,
                QColor(255, 130, 30, 22),
            ),

            # Зелёный акцент — заметно слабее, чем сейчас
            (
                0.82 + 0.04 * math.sin(t * 0.12),
                0.20 + 0.03 * math.cos(t * 0.13),
                0.48,
                QColor(55, 170, 65, 18),
            ),

            # Очень мягкий тёмно-зелёный рядом
            (
                0.88 + 0.03 * math.cos(t * 0.10),
                0.38 + 0.03 * math.sin(t * 0.12),
                0.42,
                QColor(25, 100, 35, 10),
            ),

            # Розово-фиолетовый снизу слева
            (
                0.15 + 0.04 * math.cos(t * 0.13),
                0.80 + 0.03 * math.sin(t * 0.11),
                0.50,
                QColor(210, 45, 180, 24),
            ),

            # Более глубокий фиолетовый слева
            (
                0.08 + 0.03 * math.sin(t * 0.10),
                0.46 + 0.04 * math.cos(t * 0.12),
                0.42,
                QColor(110, 35, 180, 18),
            ),

            # Сине-фиолетовый справа снизу — теперь заметнее
            (
                0.90 + 0.03 * math.cos(t * 0.09),
                0.86 + 0.03 * math.sin(t * 0.10),
                0.46,
                QColor(70, 95, 255, 24),
            ),

            # Ещё один лёгкий холодный слой рядом с синим
            (
                0.78 + 0.03 * math.sin(t * 0.10),
                0.92 + 0.02 * math.cos(t * 0.09),
                0.36,
                QColor(90, 60, 210, 16),
            ),
        ]

        for x, y, radius_scale, color in blobs:
            center_x = width * x
            center_y = height * y
            radius = max(width, height) * radius_scale

            gradient = QRadialGradient(center_x, center_y, radius)
            gradient.setColorAt(0.0, color)

            transparent = QColor(color)
            transparent.setAlpha(0)

            gradient.setColorAt(1.0, transparent)

            painter.fillRect(
                self.rect(),
                QBrush(gradient),
            )