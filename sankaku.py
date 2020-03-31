import asyncio, aiohttp, os
from time import time
from lxml import etree
from bs4 import BeautifulSoup
from tqdm import tqdm

ids = []
good_ids = []
hrefs = []
fail_url_list = []
n = 0
start_date = input('输入开始日期（例：2017-07-01）：')
end_date = input('输入结束日期（例：2017-08-01）：')
url = f'https://idol.sankakucomplex.com/?tags=date%3A{start_date}..{end_date}%20order%3Aquality'
# 新建文件夹
b = os.path.abspath('.') + '\\' + f'{start_date}..{end_date}' +'\\'
if not os.path.exists(b):
    os.makedirs(b)

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
            # 获取id
            await get_id(session, url, n)
            # 保存id
            save_id()
            # 获取url
            sem = asyncio.Semaphore(4)
            tasks = [get_href(session, sem, img_id) for img_id in good_ids]
            await asyncio.gather(*tasks)
            # 保存url
            save_href()
            # 下载
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
            print(f'{len(good_ids) - len(fail_url_list)}张图片下载完成')


async def get_id(session, url, n):
    '''爬取图片id'''
    global ids
    response = await session.get(url, headers=header)
    if n == 0:
        if response.status == 200:
            print('HTTP:200 连接成功')
        else:
            print(f'HTTP:{response.status} 连接失败')
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
    await asyncio.sleep(1)
    # n为下拉次数，既一个月份的页数
    if n < 20:
        await get_id(session, next_url, n)



def save_id():
    '''保存图片id并去重'''
    global good_ids
    with open('id.txt', 'r') as f:
        old_ids = f.read().splitlines()
        print(f'已爬取{len(old_ids)}张图片')
        for i in ids:
            if i not in old_ids:
                good_ids.append(i)
        print(f'删除{len(ids)-len(good_ids)}个重复url')
    
    if good_ids:
        with open('id.txt', 'a') as f:
            for i in good_ids:
                f.write(i + '\n')
            print(f'新增{len(good_ids)}个url到文本')
    else:
        print('没有新图')


async def get_href(session, sem, img_id):
    global hrefs
    async with sem:
        print(f'开始解析：{img_id}')
        url = 'https://idol.sankakucomplex.com/post/show/' + str(img_id)
        response = await session.get(url, headers=header)
        html = await response.text()
        tree = etree.HTML(html)
        try:
            href = 'https:' + tree.xpath('//*[@id="image"]/@src')[0]
        except IndexError:
            return
        hrefs.append(href)
        await asyncio.sleep(2)


async def download(session, sem, href, fail=False):
    global fail_url_list
    async with sem:
        if '.jpg?' or '.png?' in href:
            filename = b + href.split('?')[-1] + '.jpg'
        if '.mp4?' in href:
            filename = b + href.split('?')[-1] + '.mp4'
        if '.gif?' in href:
            filename = b + href.split('?')[-1] + '.gif'
        if '.webm?' in href:
            filename = b + href.split('?')[-1] + '.webm'
        
        response = await session.get(href, headers=download_header)
        try:
            file_size = int(response.headers['content-length'])
        except Exception as e:
            print(f'{e}\n请手动打开{url}')
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
                    with tqdm(total=file_size, initial=first_byte, unit='B', unit_scale=True, desc=href.split('?')[-1], ncols=100) as pbar:
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



def save_href():
    '''保存图片url'''
    with open('href.txt', 'a') as f:
        for i in hrefs:
            f.write(i + '\n')

if __name__ == "__main__":
    start = time()
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(main())
    loop.run_until_complete(future)
    print(f'用时{int((time()-start) // 60)}分{int((time()-start) % 60)}秒')