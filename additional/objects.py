import re
import os
import sys
import time
import heroku3
import asyncio
import aiogram
import _thread
import telebot
import inspect
import calendar
import requests
import traceback
import unicodedata
from time import sleep
from bs4 import BeautifulSoup
from datetime import datetime
from unidecode import unidecode
week = {'Mon': 'Пн', 'Tue': 'Вт', 'Wed': 'Ср', 'Thu': 'Чт', 'Fri': 'Пт', 'Sat': 'Сб', 'Sun': 'Вс'}
token_error = '580232743:AAEfqNw32ob_YkiM22GtcL68jDgP1ZJ_RMU'
token_start = '456171769:AAGVaAEZTE1n4YLa-RnRmsQ60O9C31otqiI'
idDevCentre = -1001312302092


def bold(text):
    return '<b>' + str(text) + '</b>'


def under(text):
    return '<u>' + str(text) + '</u>'


def italic(text):
    return '<i>' + str(text) + '</i>'


def code(text):
    return '<code>' + str(text) + '</code>'


def secure(text):
    return re.sub('<', '&#60;', str(text))


def get_func():
    caller = inspect.currentframe().f_back.f_back
    func_name = inspect.getframeinfo(caller)[2]
    func = caller.f_locals.get(func_name, caller.f_globals.get(func_name))
    return func


def send_dev_message(name, text, tag=code, good=False):
    if good:
        bot = telebot.TeleBot(token_start)
    else:
        bot = telebot.TeleBot(token_error)
    message = bot.send_message(idDevCentre, bold(name) + ':\n' + tag(text), parse_mode='HTML')
    return message


def printer(printer_text):
    thread_name = inspect.stack()[1][3]
    logfile = open('log.txt', 'a')
    log_print_text = thread_name + '() [' + str(_thread.get_ident()) + '] ' + str(printer_text)
    logfile.write('\n' + log_time() + log_print_text)
    logfile.close()
    print(log_print_text)


def stamper(date, pattern=None):
    if pattern is None:
        pattern = '%d/%m/%Y %H:%M:%S'
    try:
        stamp = int(calendar.timegm(time.strptime(date, pattern)))
    except IndexError and Exception:
        stamp = False
    return stamp


def start_message(name, host, stamp1, text=None):
    start_text = ''
    if text:
        start_text = '\n' + str(text)
    bot = telebot.TeleBot(token_start)
    start_text = bold(name) + ' (' + code(host) + '):\n' + \
        log_time(stamp1, code) + '\n' + \
        log_time(tag=code) + start_text
    message = bot.send_message(idDevCentre, start_text, parse_mode='HTML')
    return message


def query(link, string):
    response = requests.get(link + '?embed=1')
    soup = BeautifulSoup(response.text, 'html.parser')
    is_post_not_exist = str(soup.find('div', class_='tgme_widget_message_error'))
    if str(is_post_not_exist) == 'None':
        raw = str(soup.find('div', class_='tgme_widget_message_text js-message_text')).replace('<br/>', '\n')
        text = BeautifulSoup(raw, 'html.parser').get_text()
        search = re.search(string, text, flags=re.DOTALL)
        return search
    else:
        return None


def start_main_bot(library, token):
    logfile = open('log.txt', 'w')
    text = 'Начало записи лога ' + log_time() + '\n' + \
           'Номер главного _thread: ' + str(_thread.get_ident()) + '\n' + \
           '-' * 50
    logfile.write(text)
    logfile.close()
    if library == 'async':
        return aiogram.Bot(token)
    else:
        return telebot.TeleBot(token)


def get_bot_name():
    host = 'Unknown'
    app_name = 'Undefined'
    token = os.environ.get('api')
    if token:
        connection = heroku3.from_key(token)
        for app in connection.apps():
            app_name = app.name
            if app_name.endswith('first'):
                app_name = re.sub('-first', '', app_name, 1)
                host = 'One'
            if app_name.endswith('second'):
                app_name = re.sub('-second', '', app_name, 1)
                host = 'Two'
    return app_name, host


def secure_sql(func, value=None):
    lock = True
    response = False
    while lock is True:
        try:
            if value:
                response = func(value)
            else:
                response = func()
            lock = False
        except IndexError and Exception as error:
            lock = False
            response = str(error)
            if str(error) == 'database is locked':
                lock = True
                sleep(1)
    return response


def log_time(stamp=None, tag=None, gmt=3, form=None):
    if stamp is None:
        stamp = int(datetime.now().timestamp())
    weekday = datetime.utcfromtimestamp(stamp + gmt * 60 * 60).strftime('%a')
    day = datetime.utcfromtimestamp(stamp + gmt * 60 * 60).strftime('%d')
    month = datetime.utcfromtimestamp(stamp + gmt * 60 * 60).strftime('%m')
    year = datetime.utcfromtimestamp(stamp + gmt * 60 * 60).strftime('%Y')
    hour = datetime.utcfromtimestamp(stamp + gmt * 60 * 60).strftime('%H')
    minute = datetime.utcfromtimestamp(stamp).strftime('%M')
    second = datetime.utcfromtimestamp(stamp).strftime('%S')
    date = week[weekday] + ' ' + day + '.' + month + '.' + year + ' ' + hour + ':' + minute + ':' + second + ' '
    if form == 'channel':
        date = day + '/' + month + '/' + year + ' ' + hour + ':' + minute + ':' + second
    if form == 'normal':
        date = day + '.' + month + '.' + year + ' ' + hour + ':' + minute + ':' + second
    if tag is None:
        return date
    else:
        return tag(date)


def properties_json(sheet_id):
    body = {
        'requests': [
            {
                'updateDimensionProperties': {
                    'range': {
                        'sheetId': sheet_id,
                        'dimension': 'COLUMNS',
                        'startIndex': 0,
                        'endIndex': 1
                    },
                    'properties': {
                        'pixelSize': 1650
                    },
                    'fields': 'pixelSize'
                }
            }
        ]
    }
    return body


def edit_dev_message(old_message, text):
    entities_raw = old_message.entities
    text_list = list(old_message.text)
    entities = []
    position = 0
    for i in text_list:
        true_length = len(i.encode('utf-16-le')) // 2
        while true_length > 1:
            text_list.insert(position + 1, '')
            true_length -= 1
        position += 1
    for i in entities_raw:
        entities.append(i)
    entities.reverse()
    for i in entities:
        tag = 'code'
        if i.type == 'bold':
            tag = 'b'
        elif i.type == 'italic':
            tag = 'i'
        text_list.insert(i.offset + i.length, '</' + tag + '>')
        text_list.insert(i.offset, '<' + tag + '>')
    new_text = ''.join(text_list) + text
    bot = telebot.TeleBot(token_start)
    try:
        message = bot.edit_message_text(new_text, old_message.chat.id, old_message.message_id, parse_mode='HTML')
    except IndexError and Exception:
        new_text += italic('\nНе смог отредактировать сообщение. Отправлено новое')
        message = bot.send_message(idDevCentre, new_text, parse_mode='HTML')
    return message


def send_json(logs, name, error):
    json_text = ''
    bot = telebot.TeleBot(token_error)
    if type(logs) is str:
        for character in logs:
            replaced = unidecode(str(character))
            if replaced != '':
                json_text += replaced
            else:
                try:
                    json_text += '[' + unicodedata.name(character) + ']'
                except ValueError:
                    json_text += '[???]'
    if len(error) <= 1000:
        if json_text != '':
            doc = open(name + '.json', 'w')
            doc.write(json_text)
            doc.close()
            doc = open(name + '.json', 'rb')
            bot.send_document(idDevCentre, doc, caption=error, parse_mode='HTML')
        else:
            bot.send_message(idDevCentre, error, parse_mode='HTML')
    if 1000 < len(error) <= 4000:
        bot.send_message(idDevCentre, error, parse_mode='HTML')
    if len(error) > 4000:
        separator = 4000
        split_sep = len(error) // separator
        split_mod = len(error) / separator - len(error) // separator
        if split_mod != 0:
            split_sep += 1
        for i in range(0, split_sep):
            split_error = error[i * separator:(i + 1) * separator]
            if len(split_error) > 0:
                bot.send_message(idDevCentre, split_error, parse_mode='HTML')


def executive(library, logs):
    retry = 100
    name = secure(inspect.stack()[2][3])
    error = 'Вылет ' + bold(name + '()') + '\n\n'
    exc_type, exc_value, exc_traceback = sys.exc_info()
    error_raw = traceback.format_exception(exc_type, exc_value, exc_traceback)
    if library == 'async':
        search_retry = 'Retry in (\d+) seconds'
    else:
        search_retry = '"Too Many Requests: retry after (\d+)"'
    for i in error_raw:
        error += secure(i)
        search = re.search(search_retry, str(i))
        if search:
            retry = int(search.group(1)) + 10
    if retry >= 100:
        send_json(logs, name, error)
    if logs is None:
        func = get_func()
        return {'name': name, 'retry': retry, 'function': func}
    else:
        return {'name': name, 'retry': 0, 'function': None}


def send_starting_function(status):
    if status['retry'] >= 100:
        bot = telebot.TeleBot(token_error)
        bot.send_message(idDevCentre, 'Запущен ' + bold(status['name'] + '()'), parse_mode='HTML')


def thread_exec(logs=None):
    status = executive('non-async', logs)
    sleep(status['retry'])
    if status['function']:
        _thread.start_new_thread(status['function'], ())
    send_starting_function(status)


async def async_exec(logs=None):
    status = executive('async', logs)
    await asyncio.sleep(status['retry'])
    send_starting_function(status)
