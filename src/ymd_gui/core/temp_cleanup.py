from __future__ import annotations

import logging
from pathlib import Path


logger = logging.getLogger(__name__)

TEMP_FILE_PATTERN = ".yandex-music-downloader.*.tmp"


def cleanup_temp_files(root: Path) -> int:
    if not root.exists() or not root.is_dir():
        return 0

    removed = 0

    for path in root.rglob(TEMP_FILE_PATTERN):
        try:
            if path.is_file():
                path.unlink()
                removed += 1

                logger.debug(
                    "Removed temporary file: %s",
                    path,
                )

        except OSError:
            logger.warning(
                "Failed to remove temporary file: %s",
                path,
                exc_info=True,
            )

    if removed:
        logger.info(
            "Removed %d stale temporary file(s) from %s",
            removed,
            root,
        )

    return removed