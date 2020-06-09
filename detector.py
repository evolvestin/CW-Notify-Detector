import re
import _thread
import requests
from time import sleep
from bs4 import BeautifulSoup
from datetime import datetime
from additional.objects import thread_exec as executive
from additional.objects import bold, query, printer, get_bot_name, start_message, start_main_bot

stamp1 = int(datetime.now().timestamp())
bot = start_main_bot('non-async', '659292396:AAEeJKTEU4g2168cADrQx6QmN7IzSrJX_Ok')
lot_updater_channel = 'https://t.me/lot_updater/'
server = {
    'eu': {
        'channel': 'https://t.me/ChatWarsAuction/',
        'lot_updater': 50,
        'au_post': None
    },
    'ru': {
        'channel': 'https://t.me/chatwars3/',
        'lot_updater': 51,
        'au_post': None
    }
}

for s in server:
    result = query(lot_updater_channel + str(server[s]['lot_updater']), '(.*)')
    if result:
        split_result = result.group(1).split('/')
        server[s]['au_post'] = int(split_result[0]) + 1


if server['eu']['au_post'] and server['ru']['au_post']:
    start_message(*get_bot_name(), stamp1)
else:
    additional_text = 'Нет подключения к ' + lot_updater_channel + '\n' + bold('Бот выключен')
    start_message('detector()', stamp1, additional_text)
    _thread.exit()


def former(text):
    soup = BeautifulSoup(text, 'html.parser')
    is_post_not_exist = soup.find('div', class_='tgme_widget_message_error')
    if is_post_not_exist is None:
        lot_raw = str(soup.find('div', class_='tgme_widget_message_text js-message_text')).replace('<br/>', '\n')
        au_id = re.sub('t.me/.*?/', '', soup.find('div', class_='tgme_widget_message_link').get_text())
        lot = BeautifulSoup(lot_raw, 'html.parser').get_text()
        response = au_id + '/' + re.sub('/', '&#47;', lot).replace('\n', '/')
    else:
        response = 'False'
        search_error_requests = re.search('Channel with username .*? not found', is_post_not_exist.get_text())
        if search_error_requests:
            response += 'Requests'
    return response


def detector(host):
    global server
    while True:
        try:
            sleep(0.2)
            log_text = server[host]['channel'] + str(server[host]['au_post'])
            text = requests.get(log_text + '?embed=1')
            lot = former(text.text)
            if lot.startswith('False'):
                if lot == 'FalseRequests':
                    log_text += ' Превыщены лимиты запросов'
                else:
                    log_text += ' Лота еще нет'
            else:
                try:
                    bot.edit_message_text(lot, -1001376067490, server[host]['lot_updater'])
                    server[host]['au_post'] += 1
                    log_text += ' записан'
                except IndexError and Exception as error:
                    log_text += ' (пост не изменился'
                    search = re.search('"Too Many Requests: retry after (\d+)"', str(error))
                    if search:
                        sleep(int(search.group(1)))
                        log_text += ', слишком много запросов)'
                    else:
                        log_text += ')'
            printer(log_text)
        except IndexError and Exception:
            executive()


def telegram_polling():
    try:
        bot.polling(none_stop=True, timeout=60)
    except IndexError and Exception:
        bot.stop_polling()
        sleep(1)
        telegram_polling()


if __name__ == '__main__':
    _thread.start_new_thread(detector, ('eu',))
    _thread.start_new_thread(detector, ('ru',))
    telegram_polling()
