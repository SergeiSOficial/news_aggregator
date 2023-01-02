import random
import asyncio
from collections import deque
import httpx
from scrapy.selector import Selector
from bs4 import BeautifulSoup

from utils import random_user_agent_headers

def remove_newline(value):
    return ''.join(value.splitlines())
 

async def tralee_parser(httpx_client, posted_q, n_test_chars=50, 
                     timeout=63, check_pattern_func=None, 
                     send_message_func=None, logger=None):
    '''Кастомный парсер сайта traleetoday.ie'''
    bcs_link = 'http://traleetoday.ie/'
    source = 'traleetoday.ie'
    print("start parser")

    while True:
        try:
            response = await httpx_client.get(bcs_link, headers=random_user_agent_headers())
            response.raise_for_status()
        except Exception as e:
            if not (logger is None):
                logger.error(f'{source} error pass\n{e}')
                print("error pass")

            await asyncio.sleep(timeout*2 + random.uniform(0, 0.5))
            continue

        selector = Selector(text=response.text)
        # get news from website
        lastnews = selector.xpath('//div[contains(@class, "item post-")]')
        # print("news", len(lastnews))
        if len(lastnews) == 0:
            if not (logger is None):
                logger.error(f'{source} empty pass')
                print("empty pass")

            await asyncio.sleep(timeout*2 + random.uniform(0, 0.5))
            continue
        
        for row in lastnews:
            try:
                link = row.xpath('.//a/@href').extract_first()
            except Exception as e:
                if not (logger is None):
                    logger.error(f'{source} error pass\n{e}')
                continue
            
            try:
                news_response = await httpx_client.get(link, headers=random_user_agent_headers())
                news_response.raise_for_status()
            except Exception as e:
                if not (logger is None):
                    logger.error(f'{link} error pass\n{e}')
                    print("error pass")
                await asyncio.sleep(timeout*2 + random.uniform(0, 0.5))
                continue

            selector = Selector(text=news_response.text)
            title = selector.xpath('.//h1[@class="title"]/a[@rel="bookmark"]/text()').extract_first()
            # bold title
            title = "<b>" + title + "</b>"
            summary = selector.xpath('.//div[@class="entry"]/p[not(contains(@class, "wp-caption aligncenter"))]/text()').extract()
            img_url = selector.xpath('.//div[@class="entry"]//div[contains(@class, "wp-caption aligncenter")]/img[not(contains(@src, "-Insert-"))]/@src').extract()
            # print("img_url", img_url)
            # select only first 10 images
            if img_url:
                if len(img_url[0]) > 4:
                    if len(img_url) > 10:
                        img_url = img_url[:10]
            # print("img_url", img_url)
            post_text = ' '.join(summary[:-1])

            news_text = f'{title}\n{post_text}\n{link}'
            
            cont = ''
            # delete sentences in post_text to reduce length to 4095
            while (len(news_text)>= 1024-12):
                post_text = ' '.join(post_text.split(' ')[:-1])
                news_text = f'{title}\n{post_text}\n{link}'
                cont = 'Continue...'
            news_text = f'{title}\n{post_text}\n{cont}\n{link}'
            
            

            if len(news_text) < n_test_chars:
                continue
            
            news_text_for_head = remove_newline(news_text)
            soup = BeautifulSoup(news_text_for_head.strip(), 'html.parser')
            head_full = soup.text
            
            head = head_full[:n_test_chars].strip()
            
            # print("news_text", head)
            if head in posted_q:
                await asyncio.sleep(timeout + random.uniform(0, 0.5) + 1)
                continue

            if send_message_func is None:
                print(news_text, '\n')
            else:
                await send_message_func(news_text,img_url)

            posted_q.appendleft(head)

            await asyncio.sleep(timeout + random.uniform(0, 0.5))
        await asyncio.sleep(timeout + random.uniform(0, 0.5))

    
    


async def kerry_parser(httpx_client, posted_q, n_test_chars=50, 
                     timeout=35, check_pattern_func=None, 
                     send_message_func=None, logger=None):
    '''Кастомный парсер сайта https://www.radiokerry.ie/'''
    bcs_link = 'https://www.radiokerry.ie/'
    source = 'www.radiokerry.ie'
    print("start parser")

    while True:
        try:
            response = await httpx_client.get(bcs_link, headers=random_user_agent_headers())
            response.raise_for_status()
        except Exception as e:
            if not (logger is None):
                logger.error(f'{source} error pass\n{e}')
                print("error pass")

            await asyncio.sleep(timeout*2 + random.uniform(0, 0.5))
            continue
        # print("response ok")

        selector = Selector(text=response.text)
        # get news from website
        lastnews = selector.xpath('//div[contains(@class, "mb-8")]')
        # print("news", len(lastnews))
        if len(lastnews) == 0:
            if not (logger is None):
                logger.error(f'{source} empty pass')
                print("empty pass")

            await asyncio.sleep(timeout*2 + random.uniform(0, 0.5))
            continue
        # print("lastnews len", len(lastnews))
        # print("lastnews ok", lastnews)
        
        for row in lastnews:
            try:
                link = row.xpath('.//a/@href').extract_first()
                # print(link)
            except Exception as e:
                if not (logger is None):
                    logger.error(f'{source} error pass\n{e}')
                continue
            
            try:
                news_response = await httpx_client.get(link, headers=random_user_agent_headers())
                news_response.raise_for_status()
            except Exception as e:
                if not (logger is None):
                    logger.error(f'{link} error pass\n{e}')
                    print("error pass")
                await asyncio.sleep(timeout*2 + random.uniform(0, 0.5))
                continue

            selector = Selector(text=news_response.text)
            title = selector.xpath('.//h1/text()').extract_first()
            # bold title
            title = "<b>" + title + "</b>"
            summary = selector.xpath('.//div[contains(@class, "prose")]//p/text()').extract()
            img_url = selector.xpath('.//img/@src').extract_first()
            
            # print("img_url", img_url)
            # select only first 10 images
            if img_url:
                if len(img_url[0]) > 2:
                    if len(img_url) > 10:
                        img_url = img_url[:10]
            # print("img_url", img_url)
            post_text = ' '.join(summary[:-1])
            # print(post_text)
            news_text = f'{title}\n{post_text}\n{link}'
            # delete sentences in post_text to reduce length to 4095
            cont = ''
            while (len(news_text)>= 1024-12):
                post_text = ' '.join(post_text.split(' ')[:-1])
                news_text = f'{title}\n{post_text}\n{link}'
                cont = 'Continue...'
            news_text = f'{title}\n{post_text}\n{cont}\n{link}'
            # print("news_text", news_text)
            
            

            if len(news_text) < n_test_chars:
                continue
            
            news_text_for_head = remove_newline(news_text)
            soup = BeautifulSoup(news_text_for_head.strip(), 'html.parser')
            head_full = soup.text
            
            head = head_full[:n_test_chars].strip()
            
            # print("news_text", head)
            if head in posted_q:
                await asyncio.sleep(timeout + random.uniform(0, 0.5) + 1)
                continue
            

            if send_message_func is None:
                print(news_text, '\n')
            else:
                await send_message_func(news_text,img_url)

            posted_q.appendleft(head)

            await asyncio.sleep(timeout + random.uniform(0, 0.5) + 1)
        await asyncio.sleep(timeout + random.uniform(0, 0.5) + 2)




if __name__ == "__main__":

    # # Очередь из уже опубликованных постов, чтобы их не дублировать
    posted_tralee_q = deque(maxlen=20)

    httpx_client_tralee = httpx.AsyncClient()
    # Очередь из уже опубликованных постов, чтобы их не дублировать
    posted_kerry_q = deque(maxlen=20)
    httpx_client_kerry = httpx.AsyncClient()
    # run tralee parser and kerry parser in parallel
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(tralee_parser(httpx_client_tralee, posted_tralee_q, n_test_chars=50, 
                     timeout=7, check_pattern_func=None, 
                     send_message_func=None, logger=None),
    kerry_parser(httpx_client_kerry, posted_kerry_q, n_test_chars=50, 
                     timeout=7, check_pattern_func=None, 
                     send_message_func=None, logger=None)))
    loop.close()

    # # Закрываем соединение
    httpx_client_tralee.close()
    httpx_client_kerry.close()
    
