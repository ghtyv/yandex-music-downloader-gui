from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


def _ffmpeg_candidates() -> list[Path]:
    executable_dir = (
        Path(sys.executable)
        .resolve()
        .parent
    )

    package_root = (
        Path(__file__)
        .resolve()
        .parents[1]
    )

    if os.name == "nt":
        return [
            executable_dir
            / "resources"
            / "ffmpeg"
            / "windows"
            / "ffmpeg.exe",

            package_root
            / "resources"
            / "ffmpeg"
            / "windows"
            / "ffmpeg.exe",
        ]

    return [
        executable_dir
        / "resources"
        / "ffmpeg"
        / "linux"
        / "ffmpeg",

        package_root
        / "resources"
        / "ffmpeg"
        / "linux"
        / "ffmpeg",
    ]


def configure_ffmpeg() -> Path | None:
    for executable in _ffmpeg_candidates():
        if executable.is_file():
            directory = executable.parent

            os.environ["PATH"] = (
                str(directory)
                + os.pathsep
                + os.environ.get("PATH", "")
            )

            return executable

    system_ffmpeg = shutil.which("ffmpeg")

    if system_ffmpeg:
        return Path(system_ffmpeg)

    return None


def check_ffmpeg(
    ffmpeg_path: Path,
) -> bool:
    try:
        result = subprocess.run(
            [
                str(ffmpeg_path),
                "-version",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=5,
            check=False,
            creationflags=(
                subprocess.CREATE_NO_WINDOW
                if os.name == "nt"
                else 0
            ),
        )

        return result.returncode == 0

    except (
        OSError,
        subprocess.SubprocessError,
    ):
        return False