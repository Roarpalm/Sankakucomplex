import asyncio, aiohttp, aiofiles
from time import time
from lxml import etree

bad_ids = []
header = {
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Host': 'idol.sankakucomplex.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'
}

async def get_href(session, sem, img_id, fail=False):
    '''获取url'''
    global bad_ids
    async with sem:
        url = 'https://idol.sankakucomplex.com/post/show/' + str(img_id)
        try:
            response = await session.get(url, headers=header)
        except:
            # 请求失败等待10秒再次请求
            print('connect error...try again...')
            await asyncio.sleep(10)
            response = await session.get(url, headers=header)
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
                bad_ids.remove(img_id)
        except IndexError:
            print('Error 429 too many requests - please slow down...')
            if not fail:
                bad_ids.append(img_id)
            await asyncio.sleep(150)
            return
        if href not in old_hrefs:
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

async def main():
    async with aiohttp.connector.TCPConnector(limit=300, force_close=True, enable_cleanup_closed=True, verify_ssl=False) as tc:
        async with aiohttp.ClientSession(connector=tc) as session:
            global old_hrefs, good_ids
            with open('all href.txt', 'r') as f:
                old_hrefs = f.read().splitlines()
                print(f'已爬取{len(old_hrefs)}次')

            with open('id.txt', 'r') as f:
                good_ids = f.read().splitlines()
                n = 0
                for i in good_ids:
                    if i:
                        n += 1
                print(f'即将爬取{n}个url...')

            sem = asyncio.Semaphore(5)
            tasks = [get_href(session, sem, img_id) for img_id in good_ids if img_id]
            await asyncio.gather(*tasks)

            for _ in range(5):
                if bad_ids:
                    print('开始重新获取...')
                    tasks = [get_href(session, sem, img_id, fail=True) for img_id in bad_ids]
                    await asyncio.gather(*tasks)
                else:
                    break

def run_main():
    '''运行'''
    try:
        loop = asyncio.get_event_loop()
        future = asyncio.ensure_future(main())
        loop.run_until_complete(future)
    except (aiohttp.client_exceptions.ClientConnectionError, asyncio.exceptions.TimeoutError):
        print('网络连接中断，请再次尝试')
        input('回车以结束程序...')


if __name__ == "__main__":
    start = time()
    run_main()
    print(f'用时{int((time()-start) // 60)}分{int((time()-start) % 60)}秒')