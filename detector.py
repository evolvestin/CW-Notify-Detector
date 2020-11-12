import os
import re
import objects
import _thread
import requests
from time import sleep
from bs4 import BeautifulSoup
stamp1 = objects.time_now()

idMe = 396978030
Auth = objects.AuthCentre(os.environ['TOKEN'])
lot_updater_channel = 'https://t.me/lot_updater/'
server = {
    'eu': {
        'channel': 'https://t.me/ChatWarsAuction/',
        'lot_updater': 80,
        'au_post': None
    },
    'ru': {
        'channel': 'https://t.me/chatwars3/',
        'lot_updater': 85,
        'au_post': None
    }
}

for s in server:
    result = objects.query(lot_updater_channel + str(server[s]['lot_updater']), '(.*)')
    if result:
        split_result = result.group(1).split('/')
        server[s]['au_post'] = int(split_result[0]) + 1

executive = Auth.thread_exec
bot = Auth.start_main_bot('non-async')
if server['eu']['au_post'] and server['ru']['au_post']:
    Auth.start_message(stamp1)
else:
    additional_text = 'Нет подключения к ' + lot_updater_channel + '\n' + objects.bold('Бот выключен')
    Auth.start_message(stamp1, additional_text)
    _thread.exit()


def former(text, link):
    response = 'False'
    link = '<a href="' + link + '">'
    soup = BeautifulSoup(text, 'html.parser')
    is_post_not_exist = soup.find('div', class_='tgme_widget_message_error')
    if is_post_not_exist is None:
        lot_raw = str(soup.find('div', class_='tgme_widget_message_text js-message_text')).replace('<br/>', '\n')
        get_au_id = soup.find('div', class_='tgme_widget_message_link')
        if get_au_id:
            au_id = re.sub('t.me/.*?/', '', get_au_id.get_text())
            lot = BeautifulSoup(lot_raw, 'html.parser').get_text()
            response = link + au_id + '</a>/' + re.sub('/', '&#38;#47;', lot).replace('\n', '/')
    if is_post_not_exist:
        search_error_requests = re.search('Channel with username .*? not found', is_post_not_exist.get_text())
        if search_error_requests:
            response += 'Requests'
    return response


def detector(host):
    global server
    while True:
        try:
            sleep(0.3)
            log_text = server[host]['channel'] + str(server[host]['au_post'])
            text = requests.get(log_text + '?embed=1')
            lot = former(text.text, log_text)
            if lot.startswith('False'):
                if lot == 'FalseRequests':
                    log_text += ' Превышены лимиты запросов'
                else:
                    log_text = None
            else:
                try:
                    bot.edit_message_text(lot, -1001376067490, server[host]['lot_updater'],
                                          disable_web_page_preview=True, parse_mode='HTML')
                    server[host]['au_post'] += 1
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
            if log_text:
                objects.printer(log_text)
        except IndexError and Exception:
            executive()


@bot.message_handler(func=lambda message: message.text)
def repeat_all_messages(message):
    try:
        if message.chat.id != idMe:
            bot.send_message(message.chat.id, 'К тебе этот бот не имеет отношения, уйди пожалуйста')
        else:
            if message.text.startswith('/log'):
                bot.send_document(idMe, open('log.txt', 'rt'))
    except IndexError and Exception:
        executive(str(message))


def telegram_polling():
    try:
        bot.polling(none_stop=True, timeout=60)
    except IndexError and Exception:
        bot.stop_polling()
        sleep(1)
        telegram_polling()


if __name__ == '__main__':
    for host_channel in ['eu', 'ru']:
        _thread.start_new_thread(detector, (host_channel,))
    telegram_polling()
