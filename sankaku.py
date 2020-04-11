import tkinter as tk
import tkinter.messagebox
import asyncio, aiohttp, aiofiles, os
from time import time, sleep
from lxml import etree
from tqdm import tqdm
from bs4 import BeautifulSoup


class first():
    '''爬排行榜，获取id'''
    def __init__(self):
        self.ids = []
        self.good_ids = []
        self.n = 0
        self.start_date = e1.get()
        self.end_date = e2.get()
        self.url = f'https://idol.sankakucomplex.com/?tags=date%3A{self.start_date}..{self.end_date}%20order%3Aquality'

        start = time()
        try:
            loop = asyncio.get_event_loop()
            future = asyncio.ensure_future(self.main())
            loop.run_until_complete(future)
        except (aiohttp.client_exceptions.ClientConnectionError, asyncio.exceptions.TimeoutError):
            tkinter.messagebox.showerror(title='错误', message='网络连接中断，请再次尝试第一步')
            return
        print(f'用时{int((time()-start) // 60)}分{int((time()-start) % 60)}秒')
        tkinter.messagebox.showinfo(title='Hi!', message='第一步已完成')

    async def main(self):
        async with aiohttp.connector.TCPConnector(limit=300, force_close=True, enable_cleanup_closed=True, verify_ssl=False) as tc:
            async with aiohttp.ClientSession(connector=tc) as session:
                self.create_txt()
                await self.get_id(session, self.url, self.n)
                self.save_id()
            
    async def get_id(self, session, url, n):
        '''爬取图片id'''
        try:
            response = await session.get(url, headers=header)
        except:
            print('connect error...try again...')
            await asyncio.sleep(10)
            response = await session.get(url, headers=header)
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
        try:
            if self.n == 0:
                next_page = tree.xpath('//*[@id="post-list"]/div[3]/div[1]/@next-page-url')[0]
            else:
                next_page = tree.xpath('/html/body/div/@next-page-url')[0]
        except AttributeError:
            return
        self.n += 1
        next_url = 'https://idol.sankakucomplex.com/post/index.content' + next_page
        await asyncio.sleep(3)
        # n为下拉次数，既一个月份的页数
        if self.n < 40:
            await self.get_id(session, next_url, self.n)

    def create_txt(self):
        '''首次运行创建文本文件'''
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
            with open('id.txt', 'a') as f:
                for i in self.good_ids:
                    f.write(i + '\n')
                print(f'新增{len(self.good_ids)}个url到文本')
            # 备份
            with open('all id.txt', 'a') as f:
                f.write(f'{self.start_date}..{self.end_date}:\n')
                for i in self.good_ids:
                    f.write(i + '\n')



class second():
    '''通过id获取url'''
    def __init__(self):
        self.bad_ids = []
        with open('all href.txt', 'r') as f:
            self.old_hrefs = f.read().splitlines()
            print(f'已爬取{len(self.old_hrefs)}次')
        self.run_main()

    def run_main(self):
        start = time()
        try:
            loop = asyncio.get_event_loop()
            future = asyncio.ensure_future(self.main())
            loop.run_until_complete(future)
        except (aiohttp.client_exceptions.ClientConnectionError, asyncio.exceptions.TimeoutError):
            sleep(10)
            with open('id.txt', 'r') as f:
                new_id = f.read().splitlines()
                true_id = []
                for i in new_id:
                    if i:
                        true_id.append(i)
            with open('href.txt', 'w') as f:
                for i in true_id:
                    f.write(i + '\n')
            self.run_main()
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
            url = 'https://idol.sankakucomplex.com/post/show/' + img_id
            try:
                response = await session.get(url, headers=header)
            except:
                # 请求失败等待10秒再次请求
                print('connect error...try again...')
                await asyncio.sleep(10)
                response = await session.get(url, headers=header)
            if response.status != 200:
                # 请求过于频繁，等待150秒
                print('Error 429 too many requests - please slow down...')
                if not fail:
                    self.bad_ids.append(img_id)
                await asyncio.sleep(150)
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



class third():
    '''通过url下载文件'''
    def __init__(self):
        self.fail_url_list = []
        self.name = f'{e1.get()}..{e2.get()}'
        self.download_header = {
            'Sec-Fetch-Dest': 'document',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'}
        self.run_main()

    def run_main(self):
        start = time()
        try:
            loop = asyncio.get_event_loop()
            future = asyncio.ensure_future(self.main())
            loop.run_until_complete(future)
        except (aiohttp.client_exceptions.ClientConnectionError, asyncio.exceptions.TimeoutError):
            # 清除空行
            with open('href.txt', 'r') as f:
                all_href = f.read().splitlines()
                true_href = []
                for i in all_href:
                    if i:
                        true_href.append(i)
            with open('href.txt', 'w') as f:
                for i in true_href:
                    f.write(i + '\n')
            self.run_main()
        print(f'用时{int((time()-start) // 60)}分{int((time()-start) % 60)}秒')
        tkinter.messagebox.showinfo(title='Hi!', message='第三步已完成')

    async def main(self):
        async with aiohttp.connector.TCPConnector(limit=300, force_close=True, enable_cleanup_closed=True, verify_ssl=False) as tc:
            async with aiohttp.ClientSession(connector=tc) as session:
                # 新建文件夹
                self.new_dir()
                # 读取href
                with open('href.txt', 'r') as f:
                    hrefs = f.read().splitlines()
                # 下载
                sem = asyncio.Semaphore(5)
                tasks = [self.download(session, sem, href) for href in hrefs if href]
                await asyncio.gather(*tasks)
                # 失败重新下载
                for _ in range(3):
                    if self.fail_url_list:
                        print('开始重新下载...')
                        tasks = [self.download(session, sem, href, fail=True) for href in self.fail_url_list]
                        await asyncio.gather(*tasks)
                    else:
                        break

    def new_dir(self):
        '''新建文件夹'''
        self.b = os.path.abspath('.') + os.sep + self.name + os.sep
        self.mp4 = os.path.abspath('.') + os.sep + self.name + os.sep + 'mp4' + os.sep
        self.webm = os.path.abspath('.') + os.sep + self.name + os.sep + 'webm' + os.sep
        self.gif = os.path.abspath('.') + os.sep + self.name + os.sep + 'gif' + os.sep
        if not os.path.exists(self.b):
            os.makedirs(self.b)
        if not os.path.exists(self.mp4):
            os.makedirs(self.mp4)
        if not os.path.exists(self.gif):
            os.makedirs(self.gif)
        if not os.path.exists(self.webm):
            os.makedirs(self.webm)



    async def download(self,session, sem, href, fail=False):
        '''下载'''
        async with sem:
            if '.jpg?' or '.png?' in href:
                filename = self.b + href.split('=')[-1] + '.jpg'
            if '.mp4?' in href:
                filename = self.mp4 + href.split('=')[-1] + '.mp4'
            if '.gif?' in href:
                filename = self.gif + href.split('=')[-1] + '.gif'
            if '.webm?' in href:
                filename = self.webm + href.split('=')[-1] + '.webm'
            
            response = await session.get(href, headers=self.download_header)
            try:
                file_size = int(response.headers['content-length'])
                # 大于20M的文件不下载
                if file_size > 20000000:
                    return
            except Exception as e:
                print(f'{e}\n请手动打开{href}')
            else:
                if os.path.exists(filename):
                    # 读取文件大小
                    first_byte = os.path.getsize(filename)
                else:
                    first_byte = 0
                if first_byte >= file_size:
                    print('已存在')
                    async with aiofiles.open('href.txt', 'r+') as f:
                        read_data = await f.read()
                        await f.seek(0)
                        await f.truncate()
                        await f.write(read_data.replace(href, ''))
                    return
                # 从断点继续下载
                download_header_ = {
                    'Sec-Fetch-Dest': 'document',
                    'Upgrade-Insecure-Requests': '1',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
                    'Range': f'bytes={first_byte}-{file_size}'}
                try:
                    response = await session.get(href, headers=download_header_)
                    with open(filename, 'ab') as f:
                        with tqdm(total=file_size, initial=first_byte, unit='B', unit_scale=True, desc=href.split('=')[-1], ncols=85) as pbar:
                            while True:
                                chunk = await response.content.read(1024)
                                if not chunk:
                                    break
                                f.write(chunk)
                                pbar.update(len(chunk))
                    if fail:
                        self.fail_url_list.remove(href)

                    async with aiofiles.open('href.txt', 'r+') as f:
                        read_data = await f.read()
                        await f.seek(0)
                        await f.truncate()
                        await f.write(read_data.replace(href, ''))

                except Exception as e:
                    if not fail:
                        # 保存下载失败的url在fail_url_list
                        self.fail_url_list.append(href)

header = {
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Host': 'idol.sankakucomplex.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'}

win=tk.Tk() # 构造窗体
win.title('Sankaku') # 给窗口的可视化起名字
win.geometry('400x200')  # 设定窗口的大小(长 * 宽)
# 文字
l1 = tk.Label(win, text='开始日期：',font=('pingfang', 12))
l1.place(x=80,y=30,anchor='s')
l2 = tk.Label(win, text='结束日期：',font=('pingfang', 12))
l2.place(x=260,y=30,anchor='s')
# 输入框
e1 = tk.Entry(win, show=None)
e1.place(x=110,y=60,anchor='s')
e2 = tk.Entry(win, show=None)
e2.place(x=290,y=60,anchor='s')
# 按钮
b1 = tk.Button(win, text='第一步', font=('pingfang', 12), width=12, height=2, command=first)
b1.place(x=80,y=180,anchor='s')
b2 = tk.Button(win, text='第二步', font=('pingfang', 12), width=12, height=2, command=second)
b2.place(x=200,y=180,anchor='s')
b3 = tk.Button(win, text='第三步', font=('pingfang', 12), width=12, height=2, command=third)
b3.place(x=320,y=180,anchor='s')
# 进入消息循环
win.mainloop()