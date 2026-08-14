import keyring
from keyring.errors import PasswordDeleteError


SERVICE_NAME = "Yandex Music Downloader GUI"
TOKEN_NAME = "yandex-music-oauth-token"


def save_token(token: str) -> None:
    token = token.strip()

    if not token:
        raise ValueError("Пустой OAuth-токен.")

    keyring.set_password(
        SERVICE_NAME,
        TOKEN_NAME,
        token,
    )


def load_token() -> str | None:
    token = keyring.get_password(
        SERVICE_NAME,
        TOKEN_NAME,
    )

    if not token:
        return None

    return token.strip()


def delete_token() -> None:
    try:
        keyring.delete_password(
            SERVICE_NAME,
            TOKEN_NAME,
        )
    except PasswordDeleteError:
        pass