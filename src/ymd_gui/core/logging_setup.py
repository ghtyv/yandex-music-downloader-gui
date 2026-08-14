from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from PySide6.QtCore import QStandardPaths


LOG_FILE_NAME = "debug.log"


def configure_logging() -> Path:
    app_data = QStandardPaths.writableLocation(
        QStandardPaths.StandardLocation.AppLocalDataLocation
    )

    log_dir = Path(app_data) / "logs"
    log_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    log_path = log_dir / LOG_FILE_NAME

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # При повторном вызове не добавляем второй handler.
    for handler in root_logger.handlers:
        if (
            isinstance(handler, RotatingFileHandler)
            and Path(handler.baseFilename) == log_path
        ):
            return log_path

    handler = RotatingFileHandler(
        log_path,
        maxBytes=2 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )

    handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | "
        "%(name)s | %(threadName)s | %(message)s"
    )

    handler.setFormatter(formatter)

    root_logger.addHandler(handler)

    logging.captureWarnings(True)

    return log_path