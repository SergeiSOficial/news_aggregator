import random
import asyncio
from collections import deque
import httpx
from scrapy.selector import Selector
import urllib.request
from PIL import Image


from utils import random_user_agent_headers


async def bcs_parser(httpx_client, posted_q, n_test_chars=50, 
                     timeout=300, check_pattern_func=None, 
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
        news = selector.xpath('//div[@class="recent-post"]')
        print("news", len(news))
        if len(news) == 0:
            if not (logger is None):
                logger.error(f'{source} empty pass')
                print("empty pass")

            await asyncio.sleep(timeout*2 + random.uniform(0, 0.5))
            continue
  
       
        for row in news:
            try:
                link = row.xpath('.//a[@rel="bookmark"]/@href').extract_first()
                title = row.xpath('.//a[@rel="bookmark"]/text()').extract_first()
                summary = row.xpath('.//div[@class="entry"]/p/text()').extract_first()
                img_url = row.xpath('.//img[@class="Thumbnail thumbnail "]/@src').extract_first()
                # print(title, link, summary)
            except Exception as e:
                if not (logger is None):
                    logger.error(f'{source} error pass\n{e}')
                continue
            title = "\033[1m" + title + "\033[0m"
            news_text = f'{title}\n{summary}\n{link}'

            head = news_text[:n_test_chars].strip()

            if head in posted_q:
                continue

            if send_message_func is None:
                print(news_text, '\n')
                urllib.request.urlretrieve(img_url,"gfg.png")
                
                img = Image.open("gfg.png")
                img.show()
            else:
                await send_message_func(news_text, img_url)

            posted_q.appendleft(head)

        await asyncio.sleep(timeout + random.uniform(0, 0.5))


if __name__ == "__main__":

    # Очередь из уже опубликованных постов, чтобы их не дублировать
    posted_q = deque(maxlen=20)

    httpx_client = httpx.AsyncClient()

    asyncio.run(bcs_parser(httpx_client, posted_q))