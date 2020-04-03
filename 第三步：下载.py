# mac请将 '\\' 换成 '/'
import asyncio, aiohttp, os
from time import time
from tqdm import tqdm

fail_url_list = []
name = input('命名文件夹：')

header = {
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Host': 'idol.sankakucomplex.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'
}

download_header = {
    'Sec-Fetch-Dest': 'document',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'
}

async def main():
    async with aiohttp.connector.TCPConnector(limit=300, force_close=True, enable_cleanup_closed=True, verify_ssl=False) as tc:
        async with aiohttp.ClientSession(connector=tc) as session:
            # 新建文件夹
            new_dir()
            # 读取href
            with open('href.txt', 'r') as f:
                hrefs = f.read().splitlines()
            # 下载
            sem = asyncio.Semaphore(5)
            tasks = [download(session, sem, href) for href in hrefs]
            await asyncio.gather(*tasks)
            # 失败重新下载
            for _ in range(3):
                if fail_url_list:
                    print('开始重新下载...')
                    tasks = [download(session, sem, href, fail=True) for href in fail_url_list]
                    await asyncio.gather(*tasks)
                else:
                    break
            # 保存莫名失败的url到文本
            if fail_url_list:
                with open('fail_sankaku.txt', 'a') as f:
                    for i in fail_url_list:
                        f.write(i + '\n')
            print(f'{len(hrefs) - len(fail_url_list)}个文件下载完成')

def new_dir():
    global b, mp4, webm, gif
    '''新建文件夹'''
    b = os.path.abspath('.') + '\\' + name +'\\'
    mp4 = os.path.abspath('.') + '\\' + name +'\\' + 'mp4\\'
    webm = os.path.abspath('.') + '\\' + name +'\\' + 'webm\\'
    gif = os.path.abspath('.') + '\\' + name +'\\' + 'gif\\'
    if not os.path.exists(b):
        os.makedirs(b)
    if not os.path.exists(mp4):
        os.makedirs(mp4)
    if not os.path.exists(gif):
        os.makedirs(gif)
    if not os.path.exists(webm):
        os.makedirs(webm)



async def download(session, sem, href, fail=False):
    '''下载'''
    global fail_url_list
    async with sem:
        if '.jpg?' or '.png?' in href:
            filename = b + href.split('=')[-1] + '.jpg'
        if '.mp4?' in href:
            filename = mp4 + href.split('=')[-1] + '.mp4'
        if '.gif?' in href:
            filename = gif + href.split('=')[-1] + '.gif'
        if '.webm?' in href:
            filename = webm + href.split('=')[-1] + '.webm'
        
        response = await session.get(href, headers=download_header)
        try:
            file_size = int(response.headers['content-length'])
        except Exception as e:
            print(f'{e}\n请手动打开{href}')
        else:
            if os.path.exists(filename):
                # 读取文件大小
                first_byte = os.path.getsize(filename)
            else:
                first_byte = 0
            if first_byte >= file_size:
                print(f'已存在\n')
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
                    fail_url_list.remove(href)
            except Exception as e:
                if fail:
                    print(f'重新下载失败，原因：{e}')
                else:
                    print(f'下载失败，原因：{e}')
                    # 保存下载失败的url在fail_url_list
                    fail_url_list.append(href)

def run_main():
    '''运行'''
    try:
        loop = asyncio.get_event_loop()
        future = asyncio.ensure_future(main())
        loop.run_until_complete(future)
    except (aiohttp.client_exceptions.ClientConnectionError, asyncio.exceptions.TimeoutError):
        print('网络连接中断，建议使用代理')
        input('回车以结束程序...')

if __name__ == "__main__":
    start = time()
    run_main()
    print(f'用时{int((time()-start) // 60)}分{int((time()-start) % 60)}秒')