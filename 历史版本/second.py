import asyncio, aiohttp, aiofiles
from time import time
from lxml import etree
import tkinter.messagebox

class second():
    def __init__(self):
        self.bad_ids = []
        self.header = {
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Host': 'idol.sankakucomplex.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'
        }
        with open('all href.txt', 'r') as f:
            self.old_hrefs = f.read().splitlines()
            print(f'已爬取{len(self.old_hrefs)}次')
        
        start = time()
        try:
            loop = asyncio.get_event_loop()
            future = asyncio.ensure_future(self.main())
            loop.run_until_complete(future)
        except (aiohttp.client_exceptions.ClientConnectionError, asyncio.exceptions.TimeoutError):
            tkinter.messagebox.showerror(title='错误', message='网络连接中断，请再次尝试第二步')
        print(f'用时{int((time()-start) // 60)}分{int((time()-start) % 60)}秒')
        tkinter.messagebox.showinfo(title='Hi!', message='第二步已完成')

    async def main(self):
        async with aiohttp.connector.TCPConnector(limit=300, force_close=True, enable_cleanup_closed=True, verify_ssl=False) as tc:
            async with aiohttp.ClientSession(connector=tc) as session:
                with open('id.txt', 'r') as f:
                    good_ids = f.read().splitlines()
                    n = 0
                    for i in good_ids:
                        if i:
                            n += 1
                    print(f'即将爬取{n}个url...')

                sem = asyncio.Semaphore(5)
                tasks = [self.get_href(session, sem, img_id) for img_id in good_ids if img_id]
                await asyncio.gather(*tasks)

                for _ in range(5):
                    if self.bad_ids:
                        print('开始重新获取...')
                        tasks = [self.get_href(session, sem, img_id, fail=True) for img_id in self.bad_ids]
                        await asyncio.gather(*tasks)
                    else:
                        break

    async def get_href(self, session, sem, img_id, fail=False):
        '''获取url'''
        async with sem:
            url = 'https://idol.sankakucomplex.com/post/show/' + str(img_id)
            try:
                response = await session.get(url, headers=self.header)
            except:
                # 请求失败等待10秒再次请求
                print('connect error...try again...')
                await asyncio.sleep(10)
                response = await session.get(url, headers=self.header)
            if response.status != 200:
                # 请求过于频繁，等待120秒
                print('Error 429 too many requests - please slow down...')
                await asyncio.sleep(120)
                return
            html = await response.text()
            tree = etree.HTML(html)
            try:
                href = 'https:' + tree.xpath('//*[@id="image"]/@src')[0]
                if fail:
                    self.bad_ids.remove(img_id)
            except IndexError:
                print('Error 429 too many requests - please slow down...')
                if not fail:
                    self.bad_ids.append(img_id)
                await asyncio.sleep(150)
                return
            if href not in self.old_hrefs:
                print(href)
                # 保存一份在href.txt
                async with aiofiles.open('href.txt', 'a') as f:
                    await f.write(href + '\n')
                    await asyncio.sleep(0.1)
                # 保存一份在all href.txt
                async with aiofiles.open('all href.txt', 'a') as f:
                    await f.write(href + '\n')
                    await asyncio.sleep(0.1)
                # 将已爬的img_id从id.txt中删除
                async with aiofiles.open('id.txt', 'r+') as f:
                    read_data = await f.read()
                    await f.seek(0)
                    await f.truncate()
                    await f.write(read_data.replace(img_id, ''))
            await asyncio.sleep(1)

if __name__ == "__main__":
    second()