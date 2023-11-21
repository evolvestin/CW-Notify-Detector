import os
import re
import asyncio
import _thread
from time import sleep
from GDrive import Drive
import functions as objects
from telethon.sync import TelegramClient, events
# =====================================================================================================================
stamp1 = objects.time_now()
if __name__ == '__main__':
    import environ
    objects.printer(f'Запуск с окружением {environ.environ}')

responses = []
Auth = objects.AuthCentre(os.environ['TOKEN'])
lot_updater_channel = 'https://t.me/lot_updater/'
server = {
    'eu': {
        'channel': 'ChatWarsAuction',
        'lot_updater': int(os.environ['EU_POST_ID']),
        'au_post': None
    },
    'ru': {
        'channel': 'chatwars3',
        'lot_updater': int(os.environ['RU_POST_ID']),
        'au_post': None
    }
}

bot = Auth.start_main_bot('non-async')
for s in server:
    result = objects.query(lot_updater_channel + str(server[s]['lot_updater']), '(.*)')
    if result:
        split_result = result.group(1).split('/')
        server[s]['au_post'] = int(split_result[0]) + 1
# =====================================================================================================================


def error_handler():
    try:
        Auth.executive(None)
    except IndexError and Exception:
        sleep(10)


def editor():
    global responses
    while True:
        try:
            if responses:
                host, message = responses.pop(0)
                if message.id and message.message and message.date:
                    log_text = f"https://t.me/{server[host]['channel']}/{message.id}"
                    link = objects.html_link(log_text, message.id)
                    text = f"{link}/{re.sub('/', '&#38;#47;', message.message)}".replace('\n', '/')
                    edit_message(host, text, log_text)
            sleep(0.05)
        except IndexError and Exception:
            error_handler()


def edit_message(host: str, text: str, log_text: str) -> None:
    try:
        bot.edit_message_text(text, -1001376067490, server[host]['lot_updater'],
                              disable_web_page_preview=True, parse_mode='HTML')
        log_text += ' записан'
        sleep(1)
    except IndexError and Exception as error:
        search = re.search(r'"Too Many Requests: retry after (\d+)"', str(error))
        if search:
            sleep(int(search.group(1)))
            edit_message(host, text, log_text)
        else:
            error_handler()
            log_text += ' (пост не изменился)'
    objects.printer(log_text)


def detector(host):
    global server, responses
    try:
        asyncio.set_event_loop(asyncio.new_event_loop())
        client = TelegramClient(os.environ['session'], int(os.environ['api_id']), os.environ['api_hash']).start()
        with client:
            objects.printer(f'Канал в работе: {server[host]}')

            @client.on(events.NewMessage(chats=server[host]['channel']))
            async def handler(response):
                responses.append([host, response.message]) if response.message else None

            client.run_until_disconnected()
    except IndexError and Exception:
        error_handler()
        _thread.start_new_thread(detector, (host,))


def start(stamp):
    objects.environmental_files()
    drive_client = Drive('google.json')
    for file in drive_client.files():
        if file['name'] == f"{os.environ['session']}.session":
            drive_client.download_file(file['id'], file['name'])

    if server['eu']['au_post'] and server['ru']['au_post']:
        Auth.start_message(stamp)
    else:
        Auth.start_message(stamp, f"Нет подключения к {lot_updater_channel}\n"
                                  f"{objects.bold('Бот выключен')}")
        _thread.exit()
    for host_channel in ['eu']:  # ['eu', 'ru']
        _thread.start_new_thread(detector, (host_channel,))
    editor()


if __name__ == '__main__':
    start(stamp1)
