# mac请将 '\\' 换成 '/'
import asyncio, aiohttp, os, shutil
from time import time
from lxml import etree
from bs4 import BeautifulSoup
from tqdm import tqdm

ids = []
good_ids = []
bad_ids = []
hrefs = []
fail_url_list = []
n = 0
start_date = input('输入开始日期（例：2020-01-01）：')
end_date = input('输入结束日期（例：2020-02-01）：')
url = f'https://idol.sankakucomplex.com/?tags=date%3A{start_date}..{end_date}%20order%3Aquality'

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
    '''主程序'''
    async with aiohttp.connector.TCPConnector(limit=300, force_close=True, enable_cleanup_closed=True, verify_ssl=False) as tc:
        async with aiohttp.ClientSession(connector=tc) as session:
            await get_id(session, url, n)
            save_id()
            sem = asyncio.Semaphore(5)
            tasks = [get_href(session, sem, img_id) for img_id in good_ids]
            await asyncio.gather(*tasks)
            save_href()
            new_dir()
            tasks = [download(session, sem, href) for href in hrefs]
            await asyncio.gather(*tasks)

async def get_id(session, url, n):
    '''爬取图片id'''
    global ids
    response = await session.get(url, headers=header)
    print(f'开始解析第{n + 1}页')
    html = await response.text()
    bf = BeautifulSoup(html, 'lxml')
    classes = bf.find_all('span', {'class':'thumb blacklisted'})
    for i in classes:
        id_ = i['id'].split('p')[-1]
        ids.append(id_)
    # 获取下一页的Query String Parameters
    tree = etree.HTML(html)
    if n == 0:
        next_page = tree.xpath('//*[@id="post-list"]/div[3]/div[1]/@next-page-url')[0]
    else:
        next_page = tree.xpath('/html/body/div/@next-page-url')[0]
    n += 1
    next_url = 'https://idol.sankakucomplex.com/post/index.content' + next_page
    # n为下拉次数，既一个月份的页数
    if n < 20:
        await get_id(session, next_url, n)

def save_id():
    '''保存图片id并去重'''
    global good_ids, old_ids
    with open('id.txt', 'r') as f:
        old_ids = f.read().splitlines()
        print(f'已爬取{len(old_ids)}次')
        for i in ids:
            if i not in old_ids:
                good_ids.append(i)
        print(f'删除{len(ids)-len(good_ids)}个重复url')
    if good_ids:
        with open('id.txt', 'a') as f:
            for i in good_ids:
                f.write(i + '\n')
            print(f'新增{len(good_ids)}个url到文本')

async def get_href(session, sem, img_id):
    '''获取url'''
    global hrefs, bad_ids
    async with sem:
        url = 'https://idol.sankakucomplex.com/post/show/' + str(img_id)
        response = await session.get(url, headers=header)
        html = await response.text()
        tree = etree.HTML(html)
        href = 'https:' + tree.xpath('//*[@id="image"]/@src')[0]
        print(href)
        hrefs.append(href)

def new_dir():
    '''新建文件夹'''
    global b, mp4, webm, gif
    b = os.path.abspath('.') + '\\' + f'{start_date}..{end_date}' +'\\'
    mp4 = os.path.abspath('.') + '\\' + f'{start_date}..{end_date}' +'\\' + 'mp4\\'
    webm = os.path.abspath('.') + '\\' + f'{start_date}..{end_date}' +'\\' + 'webm\\'
    gif = os.path.abspath('.') + '\\' + f'{start_date}..{end_date}' +'\\' + 'gif\\'
    if not os.path.exists(b):
        os.makedirs(b)
    if not os.path.exists(mp4):
        os.makedirs(mp4)
    if not os.path.exists(gif):
        os.makedirs(gif)
    if not os.path.exists(webm):
        os.makedirs(webm)

async def download(session, sem, href):
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
        file_size = int(response.headers['content-length'])
        if os.path.exists(filename):
            first_byte = os.path.getsize(filename)
        else:
            first_byte = 0
        if first_byte >= file_size:
            print(f'已存在\n')
            return
        download_header_ = {
            'Sec-Fetch-Dest': 'document',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
            'Range': f'bytes={first_byte}-{file_size}'}
        response = await session.get(href, headers=download_header_)
        with open(filename, 'ab') as f:
            with tqdm(total=file_size, initial=first_byte, unit='B', unit_scale=True, desc= href.split('=')[-1], ncols=85) as pbar:
                while True:
                    chunk = await response.content.read(1024)
                    if not chunk:
                        break
                    f.write(chunk)
                    pbar.update(len(chunk))

def save_href():
    '''保存图片url'''
    with open('href.txt', 'a') as f:
        for i in hrefs:
            f.write(i + '\n')
    print(f'{len(hrefs)}个url保存成功')

def run_main():
    '''运行'''
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(main())
    loop.run_until_complete(future)

if __name__ == "__main__":
    start = time()
    run_main()
    print(f'用时{int((time()-start) // 60)}分{int((time()-start) % 60)}秒')