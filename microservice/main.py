import httpx
import asyncio
import logging
from collections import deque

from telegram_parser import telegram_parser
# from rss_parser import rss_parser
from site_parser import tralee_parser, kerry_parser
from utils import create_logger, get_history, send_error_message
from configs.config import api_id, api_hash, tralee_chat_id, kerry_chat_id, parsers_chat_id, bot_token

import platform
# pip install python-telegram-bot --upgrade
from telegram import Update, InputMediaPhoto
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ApplicationBuilder, PicklePersistence


###########################
# Можно добавить телеграм канал, rss ссылку или изменить фильтр новостей

# rss_channels = {
#     # 'www.rbc.ru': 'https://rssexport.rbc.ru/rbcnews/news/20/full.rss',
#     # 'www.ria.ru': 'https://ria.ru/export/rss2/archive/index.xml',
#     # 'www.1prime.ru': 'https://1prime.ru/export/rss2/index.xml',
#     # 'www.interfax.ru': 'https://www.interfax.ru/rss.asp',
# }


def check_pattern_func(text):
    # '''Вибирай только посты или статьи про газпром или газ'''
    # words = text.lower().split()

    # key_words = [
    #     'Tralee',     # газпром
    #     'Kerry',     # газопровод, газофикация...
    # ]

    # for word in words:
    #     if 'new' in word and len(word) < 6:  # газ, газу, газом, газа
    #         return True

    #     for key in key_words:
    #         if key in word:
    #             return True

    # return False
    return True

###########################
# Если у парсеров много ошибок или появляются повторные новости


# 50 первых символов от поста - это ключ для поиска повторных постов
n_test_chars = 50

# Количество уже опубликованных постов, чтобы их не повторять
amount_messages = 50

# Очередь уже опубликованных постов
posted_tralee_q = deque(maxlen=amount_messages)
posted_kerry_q = deque(maxlen=amount_messages)

# +/- интервал между запросами у rss и кастомного парсеров в секундах
timeout = 300

###########################


def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')


logger = create_logger('parsers_logger')
logger.info('Start...')

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

tralee_logger = create_logger('telethon', level=logging.ERROR)
persistence = PicklePersistence(filepath="conversationbot")
# Telegram bot API token (create a bot on Telegram and get the token)
app = Application.builder().token(bot_token).persistence(persistence).build()
# proxy_url = 'http://proxy.server:3128'
# if platform.system() == 'Windows':
# app = Application.builder().token(bot_token).build()
# else:
#     app = ApplicationBuilder().token(bot_token).proxy_url(
#         proxy_url).get_updates_proxy_url(proxy_url).build()

# Log all errors
app.add_error_handler(error)


async def send_message_func(text_to_send, img_url, chat_id_to_send):
    '''Отправляет посты в канал через бот'''
    # print("text_to_send:",text_to_send)
    # print("img_url:",img_url)
    if (len(img_url) == 0):
        await app.bot.send_message(chat_id=chat_id_to_send,
                                   parse_mode='html', text=text_to_send)
    elif (len(img_url) == 1):
        await app.bot.send_photo(chat_id=chat_id_to_send,
                                 parse_mode='html', caption=text_to_send, photo=img_url[0])
    else:
        media_to_send = []
        for img in img_url:
            media_to_send.append(InputMediaPhoto(media=img))
        await app.bot.send_media_group(chat_id=chat_id_to_send, parse_mode=ParseMode.HTML,
                                       caption=text_to_send, media=media_to_send)
    logger.info(text_to_send)

# Телеграм парсер
client_tralee = telegram_parser('traleeparser', api_id, api_hash, tralee_chat_id, posted_tralee_q,
                                n_test_chars, check_pattern_func, send_message_func,
                                tralee_logger, loop)
client_kerry = telegram_parser('kerryparser', api_id, api_hash, kerry_chat_id, posted_kerry_q,
                               n_test_chars, check_pattern_func, send_message_func,
                               tralee_logger, loop)


# Список из уже опубликованных постов, чтобы их не дублировать

history_tralee = loop.run_until_complete(get_history(client_tralee, tralee_chat_id,
                                                     n_test_chars, amount_messages))
history_kerry = loop.run_until_complete(get_history(client_kerry, kerry_chat_id,
                                                    n_test_chars, amount_messages))

posted_tralee_q.extend(history_tralee)
posted_kerry_q.extend(history_kerry)
# posted_tralee_q = []
# posted_kerry_q = []

httpx_client = httpx.AsyncClient()

# Добавляй в текущий event_loop rss парсеры
# for source, rss_link in rss_channels.items():

#     # https://docs.python-guide.org/writing/gotchas/#late-binding-closures
#     async def wrapper(source, rss_link):
#         try:
#             await rss_parser(httpx_client, source, rss_link, posted_q,
#                              n_test_chars, timeout, check_pattern_func,
#                              se+353nd_message_func, logger)
#         except Exception as e:
#             message = f'&#9888; ERROR: {source} parser is down! \n{e}'
#             await send_error_message(message, bot_token, gazp_chat_id, logger)

#     loop.create_task(wrapper(source, rss_link))


# Добавляй в текущий event_loop кастомный парсер
async def tralee_wrapper():
    try:
        await tralee_parser(httpx_client, posted_tralee_q, n_test_chars, timeout,
                            check_pattern_func, send_message_func, logger)
    except Exception as e:
        message = f'&#9888; ERROR: Traleetoday parser is down! \n{e}'
        print(message,)
        print(logger)
        await send_error_message(message, bot_token, parsers_chat_id, logger)

# Добавляй в текущий event_loop кастомный парсер


async def kerry_wrapper():
    try:
        await kerry_parser(httpx_client, posted_kerry_q, n_test_chars, timeout,
                           check_pattern_func, send_message_func, logger)
    except Exception as e:
        message = f'&#9888; ERROR: Kerry parser is down! \n{e}'
        await send_error_message(message, bot_token, parsers_chat_id, logger)

# create loop
loop.create_task(tralee_wrapper())
loop.create_task(kerry_wrapper())
try:
    loop.run_forever()
except KeyboardInterrupt:
    logger.info('Stopped.')
    # client_tralee.disconnect()
    # client_kerry.disconnect()
    loop.close()
