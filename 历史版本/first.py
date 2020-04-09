import asyncio, aiohttp, os
from time import time
from lxml import etree
from bs4 import BeautifulSoup
import tkinter.messagebox
import tkinter as tk

class first():
    def __init__(self):
        self.ids = []
        self.good_ids = []
        self.n = 0
        self.start_date = input('开始日期（例：2020-01-01）：')
        self.end_date = input('结束日期（例：2020-02-01）：')
        self.url = f'https://idol.sankakucomplex.com/?tags=date%3A{self.start_date}..{self.end_date}%20order%3Aquality'
        self.header = {
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Host': 'idol.sankakucomplex.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'
        }
        
        start = time()
        try:
            loop = asyncio.get_event_loop()
            future = asyncio.ensure_future(self.main())
            loop.run_until_complete(future)
        except (aiohttp.client_exceptions.ClientConnectionError, asyncio.exceptions.TimeoutError):
            tkinter.messagebox.showerror(title='错误', message='网络连接中断，请再次尝试第一步')
        print(f'用时{int((time()-start) // 60)}分{int((time()-start) % 60)}秒')
        tkinter.messagebox.showinfo(title='Hi!', message='第一步已完成')

    async def main(self):
        async with aiohttp.connector.TCPConnector(limit=300, force_close=True, enable_cleanup_closed=True, verify_ssl=False) as tc:
            async with aiohttp.ClientSession(connector=tc) as session:
                # 创建文件
                self.create_txt()
                # 获取id
                await self.get_id(session, self.url, self.n)
                # 保存id
                self.save_id()
            
    async def get_id(self, session, url, n):
        '''爬取图片id'''
        try:
            response = await session.get(url, headers=self.header)
        except:
            print('connect error...try again...')
            await asyncio.sleep(10)
            response = await session.get(url, headers=self.header)
        if self.n == 0:
            if response.status == 200:
                print('HTTP:200 连接成功')
            else:
                print(f'HTTP:{response.status} 连接失败')
        print(f'开始解析第{n + 1}页...')
        
        html = await response.text()
        bf = BeautifulSoup(html, 'lxml')
        classes = bf.find_all('span', {'class':'thumb blacklisted'})
        for i in classes:
            id_ = i['id'].split('p')[-1]
            self.ids.append(id_)

        # 获取下一页的Query String Parameters
        tree = etree.HTML(html)
        if self.n == 0:
            next_page = tree.xpath('//*[@id="post-list"]/div[3]/div[1]/@next-page-url')[0]
        else:
            next_page = tree.xpath('/html/body/div/@next-page-url')[0]
        self.n += 1
        next_url = 'https://idol.sankakucomplex.com/post/index.content' + next_page
        await asyncio.sleep(3)
        # n为下拉次数，既一个月份的页数
        if self.n < 20:
            await self.get_id(session, next_url, self.n)

    def create_txt(self):
        id_ = 'id.txt'
        all_id_ = 'all id.txt'
        href_ = 'href.txt'
        all_href_ = 'all href.txt'
        if not os.path.exists(id_):
            f = open(id_, 'a')
            f.close()
        if not os.path.exists(all_id_):
            f = open(all_id_, 'a')
            f.close()
        if not os.path.exists(href_):
            f = open(href_, 'a')
            f.close()
        if not os.path.exists(all_href_):
            f = open(all_href_, 'a')
            f.close()

    def save_id(self):
        '''保存图片id并去重'''
        with open('all id.txt', 'r') as f:
            old_ids = f.read().splitlines()
            print(f'已爬取{len(old_ids)}次')
            for i in self.ids:
                if i not in old_ids:
                    self.good_ids.append(i)
            print(f'删除{len(self.ids)-len(self.good_ids)}个重复url')
        if self.good_ids:
            # 保存
            with open('id.txt', 'w') as f:
                for i in self.good_ids:
                    f.write(i + '\n')
                print(f'新增{len(self.good_ids)}个url到文本')
            # 备份
            with open('all id.txt', 'a') as f:
                f.write(f'{self.start_date}..{self.end_date}:')
                for i in self.good_ids:
                    f.write(i + '\n')

if __name__ == "__main__":
    first()