import httpx
import asyncio
import logging
from collections import deque
from telethon import TelegramClient

from telegram_parser import telegram_parser
# from rss_parser import rss_parser
from site_parser import tralee_parser, kerry_parser
from utils import create_logger, get_history, send_error_message
from configs.config import api_id, api_hash, tralee_chat_id, kerry_chat_id, bot_token


###########################
# Можно добавить телеграм канал, rss ссылку или изменить фильтр новостей

telegram_channels = {
    # 1099860397: 'https://t.me/rbc_news',
    # 1428717522: 'https://t.me/gazprom',
    # 1101170442: 'https://t.me/rian_ru',
    # 1133408457: 'https://t.me/prime1',
    # 1149896996: 'https://t.me/interfaxonline',
    # # 1001029560: 'https://t.me/tralee_express',
    # 1818397776: 'https://t.me/traleetoday',  # Канал аггрегатор новостей
}

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


logger = create_logger('parsers_logger')
logger.info('Start...')

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

tele_logger = create_logger('telethon', level=logging.ERROR)

bot = TelegramClient('bot', api_id, api_hash,
                     base_logger=tele_logger, loop=loop)
bot.start(bot_token=bot_token)


async def send_message_tralee_func(text, img_url):
    '''Отправляет посты в канал через бот'''
    print(text)
    print(img_url)
    if(len(img_url) > 0):
        await bot.send_message(entity=tralee_chat_id,
                            parse_mode='html', link_preview=False, message=text, file = img_url)
    else:
        await bot.send_message(entity=tralee_chat_id,
                            parse_mode='html', link_preview=False, message=text)
    logger.info(text)

async def send_message_kerry_func(text, img_url):
    '''Отправляет посты в канал через бот'''
    print(text)
    print(img_url)
    if(len(img_url) > 0):
        await bot.send_message(entity=kerry_chat_id,
                            parse_mode='html', link_preview=False, message=text, file = img_url)
    else:
        await bot.send_message(entity=kerry_chat_id,
                            parse_mode='html', link_preview=False, message=text)
    logger.info(text)


# Телеграм парсер
client_tralee = telegram_parser('traleeparser', api_id, api_hash, telegram_channels, posted_tralee_q,
                         n_test_chars, check_pattern_func, send_message_tralee_func,
                         tele_logger, loop)
client_kerry = telegram_parser('kerryparser', api_id, api_hash, telegram_channels, posted_kerry_q,
                         n_test_chars, check_pattern_func, send_message_kerry_func,
                         tele_logger, loop)


# Список из уже опубликованных постов, чтобы их не дублировать

history_tralee = loop.run_until_complete(get_history(client_tralee, tralee_chat_id,
                                              n_test_chars, amount_messages))
history_kerry = loop.run_until_complete(get_history(client_kerry, kerry_chat_id,
                                              n_test_chars, amount_messages))

posted_tralee_q.extend(history_tralee)
posted_kerry_q.extend(history_kerry)

httpx_tralee_client = httpx.AsyncClient()
# httpx_kerry_client = httpx.AsyncClient()

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
        await tralee_parser(httpx_tralee_client, posted_tralee_q, n_test_chars, timeout,
                         check_pattern_func, send_message_tralee_func, logger)
    except Exception as e:
        message = f'&#9888; ERROR: Traleetoday arser is down! \n{e}'
        await send_error_message(message, bot_token, parsers_chat_id, logger)

loop.create_task(tralee_wrapper())

# Добавляй в текущий event_loop кастомный парсер
async def kerry_wrapper():
    try:
        await kerry_parser(httpx_tralee_client, posted_kerry_q, n_test_chars, timeout,
                         check_pattern_func, send_message_kerry_func, logger)
    except Exception as e:
        message = f'&#9888; ERROR: Kerry parser is down! \n{e}'
        await send_error_message(message, bot_token, parsers_chat_id, logger)

loop.create_task(kerry_wrapper())



try:
    # run tralee client and kerry client in parallel
    # loop.run_until_complete(asyncio.gather(client_tralee(), client_kerry()))
    # client_tralee.run_until_disconnected()
    client_kerry.run_until_disconnected()


except Exception as e:
    message = f'&#9888; ERROR: telegram parser (all parsers) is down! \n{e}'
    loop.run_until_complete(send_error_message(message, bot_token,
                                               parsers_chat_id, logger))
finally:
    loop.run_until_complete(httpx_tralee_client.aclose())
    loop.close()
