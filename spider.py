import csv
import datetime
import argparse
import hashlib
import sys
from urllib.parse import quote
import execjs
import requests
from bs4 import BeautifulSoup
from playwright.async_api import BrowserContext, Page, async_playwright
import asyncio
import config
from tools import utils
from login import DianPingLogin

class DianPingSpider:

    def __init__(self, login_type: str, crawler_type: str, timeout=10):
        # self.ua = UserAgent()
        self.headers = {
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                        'Accept-Language': 'zh-CN,zh;q=0.9,ja;q=0.8,en;q=0.7,en-GB;q=0.6,en-US;q=0.5',
                        'Connection': 'keep-alive',
                        'Referer': 'https://www.dianping.com/',
                        'Sec-Fetch-Dest': 'document',
                        'Sec-Fetch-Mode': 'navigate',
                        'Sec-Fetch-Site': 'same-origin',
                        'Sec-Fetch-User': '?1',
                        'Upgrade-Insecure-Requests': '1',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0',
                        'sec-ch-ua': '"Microsoft Edge";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
                        'sec-ch-ua-mobile': '?0',
                        'sec-ch-ua-platform': '"Windows"',
                        }
        self.login_type = login_type
        self.crawler_type = crawler_type
        self.timeout = timeout
        self.playwright_page = None
        self.cookies = None

    async def start_crawling(self):
        await self.login()
        if self.crawler_type == 'detail':
            await self.get_comments_pages_id_list()
    async def login(self):
        """ login """
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)
            dplogin = DianPingLogin(login_type=self.login_type, browser=browser)
            await dplogin.begin()
            self.cookies = dplogin.cookies

    async def get_comments_pages_id(self, id: str):

        page = 1
        next_page = True
        while next_page:
            utils.logger.info(f"[DianPingSpider.get_comment_one_page] begin crawling id: {id} page: {page}")
            response = requests.get(f'https://www.dianping.com/shop/{id}/review_all/p{page}', cookies=self.cookies,
                                    headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            lis = soup.find_all('li')
            comments = []
            for li in lis:
                comment = {}
                try:
                    comment['name'] = li.find('a', class_='name').text.replace(" ", "").replace("\n", "").replace("\r", "")
                    comment['rank'] = li.find('span', class_='score').text.replace(" ", "").replace("\n", "").replace("\r", "")
                    if li.find('div', class_='review-words Hide'):
                        comment['review'] = li.find('div', class_='review-words Hide').text.replace(" ", "").replace("\n", "").replace("\r", "")
                    else:
                        comment['review'] = li.find('div', class_='review-words').text.replace(" ", "").replace("\n", "").replace("\r", "")
                    utils.logger.info(f"[DianPingSpider.get_comment_one_page] get comment: {comment['review']}")
                except Exception as e:
                    continue
                comments.append(comment)
            await self.store_csv(comments, id)
            try:
                soup.find(string='下一页')
                page += 1
                continue
            except Exception as e:
                next_page = False
        utils.logger.info(f"[DianPingSpider.get_comment_pages] id: {id} crawling finish!")

    async def get_comments_pages_id_task(self, id: str, semaphore: asyncio.Semaphore):
        async with semaphore:
            try:
                result = await self.get_comments_pages_id(id=id)
                return result
            except KeyError as ex:
                utils.logger.error(
                    f"[DianPingSpider.get_comment_one_page_task] have not fund comment detail id:{id}, err: {ex}")
                return None

    async def get_comments_pages_id_list(self, id_list = config.DIANPING_ID_LIST):

        semaphore = asyncio.Semaphore(config.MAX_CONCURRENCY_NUM)
        task_list = [
            self.get_comments_pages_id_task(id=id, semaphore=semaphore) for id in
            id_list
        ]
        await asyncio.gather(*task_list)
        utils.logger.info(f"[DianPingSpider.get_comment_pages] crawling finish!")

    async def store_csv(self, comments, id):


        file_name = 'data/' + id + '_' + str(datetime.date.today()) + '.csv'

        with open(file_name, 'a', encoding='utf-8', newline='') as f:
            w = csv.writer(f)
            # w.writerow(comments[0].keys())
            for comment in comments:
                w.writerow(comment.values())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='DianPing crawler program.')
    parser.add_argument('--lt', type=str, help='Login type (qrcode | cookie)',
                        choices=["qrcode", "cookie"], default=config.LOGIN_TYPE)
    parser.add_argument('--type', type=str, help='crawler type (search | article | question)',
                        choices=["search", "article", "question"], default=config.CRAWLER_TYPE)

    args = parser.parse_args()

    spider = DianPingSpider(login_type=args.lt, crawler_type=args.type)
    asyncio.run(spider.start_crawling())
