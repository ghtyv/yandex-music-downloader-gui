import os
import shutil
import subprocess
from pathlib import Path


def configure_ffmpeg() -> Path | None:
    package_root = Path(__file__).resolve().parents[1]

    if os.name == "nt":
        bundled_dir = (
            package_root
            / "resources"
            / "ffmpeg"
            / "windows"
        )

        executable = bundled_dir / "ffmpeg.exe"
    else:
        bundled_dir = (
            package_root
            / "resources"
            / "ffmpeg"
            / "linux"
        )

        executable = bundled_dir / "ffmpeg"

    if executable.is_file():
        os.environ["PATH"] = (
            str(bundled_dir)
            + os.pathsep
            + os.environ.get("PATH", "")
        )

        return executable

    system_ffmpeg = shutil.which("ffmpeg")

    if system_ffmpeg:
        return Path(system_ffmpeg)

    return None

def check_ffmpeg(ffmpeg_path: Path) -> bool:
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
        )

        return result.returncode == 0

    except (
        OSError,
        subprocess.SubprocessError,
    ):
        return False