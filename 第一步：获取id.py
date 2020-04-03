import asyncio, aiohttp
from time import time
from lxml import etree
from bs4 import BeautifulSoup

ids = []
good_ids = []
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

async def main():
    async with aiohttp.connector.TCPConnector(limit=300, force_close=True, enable_cleanup_closed=True, verify_ssl=False) as tc:
        async with aiohttp.ClientSession(connector=tc) as session:
            # 获取id
            await get_id(session, url, n)
            # 保存id
            save_id()
            
async def get_id(session, url, n):
    '''爬取图片id'''
    global ids
    try:
        response = await session.get(url, headers=header)
    except:
        print('connect error...try again...')
        await asyncio.sleep(10)
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
    await asyncio.sleep(3)
    # n为下拉次数，既一个月份的页数
    if n < 20:
        await get_id(session, next_url, n)



def save_id():
    '''保存图片id并去重'''
    global good_ids, old_ids
    with open('all id.txt', 'r') as f:
        old_ids = f.read().splitlines()
        print(f'已爬取{len(old_ids)}次')
        for i in ids:
            if i not in old_ids:
                good_ids.append(i)
        print(f'删除{len(ids)-len(good_ids)}个重复url')
    if good_ids:
        # 保存
        with open('id.txt', 'w') as f:
            for i in good_ids:
                f.write(i + '\n')
            print(f'新增{len(good_ids)}个url到文本')
        # 备份
        with open('all id.txt', 'a') as f:
            for i in good_ids:
                f.write(i + '\n')

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