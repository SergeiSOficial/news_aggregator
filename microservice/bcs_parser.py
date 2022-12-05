import random
import asyncio
from collections import deque
import httpx
from scrapy.selector import Selector

from utils import random_user_agent_headers


async def bcs_parser(httpx_client, posted_q, n_test_chars=50, 
                     timeout=30, check_pattern_func=None, 
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

        selector = Selector(text=response.text)
        # get news from website
        lastnews = selector.xpath('//div[contains(@class, "mb-8")]')
        print("news", len(lastnews))
        if len(lastnews) == 0:
            if not (logger is None):
                logger.error(f'{source} empty pass')
                print("empty pass")

            await asyncio.sleep(timeout*2 + random.uniform(0, 0.5))
            continue
        
        for row in lastnews:
            try:
                link = row.xpath('.//a[contains(@role, "link")]/@href').extract_first()
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
            
            print("img_url", img_url)
            # select only first 10 images
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
            head = news_text[:n_test_chars].strip()

            if len(news_text) < n_test_chars:
                continue
            
            if head in posted_q:
                continue
            

            if send_message_func is None:
                print(news_text, '\n')
            else:
                await send_message_func(news_text,img_url)

            posted_q.appendleft(head)

            await asyncio.sleep(timeout + random.uniform(0, 0.5))
        await asyncio.sleep(timeout + random.uniform(0, 0.5))


if __name__ == "__main__":

    # Очередь из уже опубликованных постов, чтобы их не дублировать
    posted_q = deque(maxlen=20)

    httpx_client = httpx.AsyncClient()

    asyncio.run(bcs_parser(httpx_client, posted_q))