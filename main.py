import asyncio
import html
import logging
import os
import sys
import time
from datetime import datetime, timezone

from aiogram import Bot
from aiogram.types import BufferedInputFile, User
from telethon import TelegramClient, events
from telethon.tl.custom import Message

from config import TELEGRAM_HOST, Config, code, configure_header, html_link
from drive_utils import GDriveManager

logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

bot = Bot(token=Config.BOT_TOKEN)


async def send_alert(text: str, escape_html: bool = True) -> None:
    """
    Sends an alert message to the configured developer chat.
    If the message is too long, it is sent as a text file attachment.

    Args:
        text: The content of the alert.
        escape_html: Whether to escape HTML characters in the text. Defaults to True.
    """
    max_retries = 6
    delay = 0.5

    for attempt in range(max_retries):
        try:
            text_str = str(text)
            if len(text_str) > 4000:
                file_data = text_str.encode('utf-8')
                document = BufferedInputFile(file_data, filename=f'alert_{int(time.time())}.txt')

                await bot.send_document(
                    chat_id=Config.DEV_CHAT_ID,
                    document=document,
                    caption=(f'{Config.ALERT_HEADER}\nLog content is too long, attached as file.'),
                    parse_mode='HTML',
                )
            else:
                await bot.send_message(
                    chat_id=Config.DEV_CHAT_ID,
                    text=(
                        f'{Config.ALERT_HEADER}\n'
                        f'{html.escape(text_str) if escape_html else text_str}'
                    ),
                    parse_mode='HTML',
                )
            return
        except Exception as e:
            if attempt == max_retries - 1:
                logger.error(f'Failed to send alert after {max_retries} attempts: {e}')
            else:
                logger.warning(f'Alert send failed: {e}. Retrying in {delay}s...')
                await asyncio.sleep(delay)
                delay = min(delay * 2, 3600)


async def update_lot_message(message: Message, host_key: str) -> None:
    """
    Updates the auction lot message in the target channel with the content from the source.
    It also updates the health check file.

    Args:
        message: The original message object from Telethon.
        host_key: The key corresponding to the source server in the configuration.
    """
    try:
        log_link = f'{TELEGRAM_HOST}{host_key}/{message.id}'
        safe_text = message.message.replace('/', '&#38;#47;').replace('\n', '/')

        await bot.edit_message_text(
            text=f'{html_link(log_link, str(message.id))}/{safe_text}',
            chat_id=Config.TARGET_CHANNEL_ID,
            message_id=Config.SERVERS[host_key]['post_id'],
            parse_mode='HTML',
            disable_web_page_preview=True,
        )
        logger.info(f'Updated post for {host_key}: {message.id}')

        with open('tmp/healthy', 'w', encoding='utf-8') as f:
            f.write(str(datetime.now().timestamp()))

    except Exception as e:
        err_msg = f'Error updating message: {e}'
        await send_alert(err_msg)
        logger.error(err_msg)


async def main() -> None:
    """
    The main entry point of the application.
    Initializes Google Drive, downloads the session, and starts the Telegram client listener.
    """
    os.makedirs('tmp', exist_ok=True)

    async with bot:
        try:
            drive = GDriveManager(Config.GOOGLE_CREDS_JSON)
            drive.download_session_file(Config.SESSION_NAME)
        except Exception as e:
            await send_alert(f'Startup failed (GDrive): {e}')
            sys.exit(1)

        client = TelegramClient(Config.SESSION_NAME, Config.API_ID, Config.API_HASH)

        @client.on(events.NewMessage(chats=list(Config.SERVERS.keys())))
        async def handler(event: events.NewMessage.Event) -> None:
            if event.message:
                chat_username: str = event.chat.username
                if chat_username in Config.SERVERS:
                    await update_lot_message(event.message, chat_username)

        try:
            await client.start()
            bot_info: User = await bot.get_me()
            if bot_info.username:
                Config.ALERT_HEADER = configure_header(bot_info.username)

            now = datetime.now(tz=timezone.utc)
            await send_alert(code(now.strftime('%Y-%m-%d %H:%M:%S')), escape_html=False)

            with open('tmp/healthy', 'w') as f:
                f.write('start')

            logger.info('Client started, listening...')
            await client.run_until_disconnected()

        except Exception as e:
            logger.critical(f'Critical error in main loop: {e}')
            await send_alert(f'CRASH: {e}')
            sys.exit(1)


def manage_crash_backoff() -> None:
    """
    Manages the delay between restarts in case of crashes using an exponential backoff strategy.
    It tracks crash attempts in a temporary state file.
    """
    state_file = 'tmp/crash_state'
    reset_window = 300
    free_attempts = 5

    now = time.time()
    attempts = 0

    if os.path.exists(state_file):
        try:
            with open(state_file, 'r', encoding='utf-8') as f:
                content = f.read().strip().split('|')
                if len(content) == 2:
                    last_ts = float(content[0])
                    prev_attempts = int(content[1])

                    if now - last_ts < reset_window:
                        attempts = prev_attempts
        except Exception:
            pass

    attempts += 1

    try:
        with open(state_file, 'w', encoding='utf-8') as f:
            f.write(f'{now}|{attempts}')
    except Exception:
        pass

    if attempts > free_attempts:
        delay = min(2 ** (attempts - free_attempts), 3600)
        logger.warning(
            f'Crash loop detected ({attempts} attempts). Backoff active: sleeping {delay}s...'
        )
        time.sleep(delay)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
    except Exception as e:
        logger.critical(f'Fatal runtime error: {e}')
    finally:
        manage_crash_backoff()
