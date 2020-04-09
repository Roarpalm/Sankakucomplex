import asyncio, aiohttp, aiofiles, os
from time import time
from tqdm import tqdm
import tkinter.messagebox

class third():
    def __init__(self):
        self.fail_url_list = []
        self.name = input('命名文件夹：')
        self.header = {
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Host': 'idol.sankakucomplex.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'}
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
            #tkinter.messagebox.showerror(title='错误', message='网络连接中断，请再次尝试第三步')
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
                    if fail:
                        print(f'重新下载失败，原因：{e}')
                    else:
                        print(f'下载失败，原因：{e}')
                        # 保存下载失败的url在fail_url_list
                        self.fail_url_list.append(href)

if __name__ == "__main__":
    third()