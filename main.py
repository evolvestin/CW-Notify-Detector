import os
import re
import asyncio
import _thread
from time import sleep
from GDrive import Drive
import functions as objects
from telethon.sync import TelegramClient, events
if __name__ == '__main__':
    import environ
    print('Запуск с окружением', environ.environ)
stamp1 = objects.time_now()
# =====================================================================================================================

responses = []
idMe = 396978030
objects.environmental_files()
drive_client = Drive('google.json')
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

for file in drive_client.files():
    if file['name'] == f"{os.environ['session']}.session":
        drive_client.download_file(file['id'], file['name'])

for s in server:
    result = objects.query(lot_updater_channel + str(server[s]['lot_updater']), '(.*)')
    if result:
        split_result = result.group(1).split('/')
        server[s]['au_post'] = int(split_result[0]) + 1

if server['eu']['au_post'] and server['ru']['au_post']:
    Auth.start_message(stamp1)
else:
    additional_text = f"Нет подключения к {lot_updater_channel}\n{objects.bold('Бот выключен')}"
    Auth.start_message(stamp1, additional_text)
    _thread.exit()
# =====================================================================================================================


def editor():
    global responses
    while True:
        try:
            if responses:
                host, message = responses.pop(0)
                if message.id and message.message and message.date:
                    log_text = f"{server[host]['channel']}/{message.id}"
                    link = objects.html_link(log_text, message.id)
                    text = f"{link}/{re.sub('/', '&#38;#47;', message.message)}".replace('\n', '/')
                    try:
                        bot.edit_message_text(text, -1001376067490, server[host]['lot_updater'],
                                              disable_web_page_preview=True, parse_mode='HTML')
                        log_text += ' записан'
                        sleep(1.2)
                    except IndexError and Exception as error:
                        log_text += ' (пост не изменился'
                        search = re.search(r'"Too Many Requests: retry after (\d+)"', str(error))
                        if search:
                            sleep(int(search.group(1)))
                            log_text += ', слишком много запросов)'
                        else:
                            log_text += ')'
                    objects.printer(log_text)
            sleep(0.05)
        except IndexError and Exception:
            Auth.executive(None)


def detector(host):
    global server
    try:
        asyncio.set_event_loop(asyncio.new_event_loop())
        client = TelegramClient(os.environ['session'], int(os.environ['api_id']), os.environ['api_hash']).start()
        with client:
            objects.printer(f'Канал в работе: {server[host]}')

            @client.on(events.NewMessage(chats=server[host]['channel']))
            async def handler(response):
                if response.message:
                    responses.append([host, response.message])

            client.run_until_disconnected()
    except IndexError and Exception:
        Auth.executive(None)
        _thread.start_new_thread(detector, (host,))


@bot.message_handler(func=lambda message: message.text)
def repeat_all_messages(message):
    try:
        if message.chat.id == idMe and message.text.startswith('/log'):
            bot.send_document(message.chat.id, open('log.txt', 'r'))
    except IndexError and Exception:
        Auth.executive(str(message))


def telegram_polling():
    try:
        bot.polling(none_stop=True, timeout=60)
    except IndexError and Exception:
        bot.stop_polling()
        sleep(1)
        telegram_polling()


def start():
    for host_channel in ['eu']:  # ['eu', 'ru']
        _thread.start_new_thread(detector, (host_channel,))
    _thread.start_new_thread(editor, ())
    telegram_polling()


if __name__ == '__main__':
    start()
