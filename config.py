import os
from typing import TypedDict

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_HOST: str = 'https://t.me/'


def code(text: str) -> str:
    """Wraps the provided text in an HTML code tag."""
    return f'<code>{text}</code>'


def html_link(link: str, text: str) -> str:
    """Creates an HTML anchor link with the specified URL and text."""
    return f'<a href="{link}">{text}</a>'


def configure_header(username: str) -> str:
    """Generates the alert header with the bot username and environment tag."""
    link = html_link(f'{TELEGRAM_HOST}{username}', 'detector')
    return f'<b>{link}</b> ({code(os.getenv("HOST_ENV", "local"))}):'


class ServerConfig(TypedDict):
    """Type definition for server configuration parameters."""

    post_id: int
    host: str


class Config:
    """Main application configuration class."""

    API_ID: int = int(os.getenv('API_ID', '0'))
    API_HASH: str = os.getenv('API_HASH', '')
    SESSION_NAME: str = os.getenv('SESSION_NAME', 'detector')

    DEV_CHAT_ID: int = -1001312302092
    TARGET_CHANNEL_ID: int = -1001376067490
    BOT_TOKEN: str = os.getenv('BOT_TOKEN', '')

    GOOGLE_CREDS_JSON: str = os.getenv('GOOGLE_CREDS_JSON', '')

    ALERT_HEADER: str = configure_header('local')

    SERVERS: dict[str, ServerConfig] = {
        'chatwars3': {'post_id': 107, 'host': 'ru'},
        'ChatWarsAuction': {'post_id': 110, 'host': 'eu'},
        'UsefullCWLinks': {'post_id': 116, 'host': 'test'},
    }
