from multiprocessing.dummy import Pool as ThreadPool
# from multiprocessing import Pool as ProcessPool
import time

from bs4 import BeautifulSoup
import requests

import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor
from contextlib import suppress


def go(url):
    rs = requests.get(url)
    if rs.status_code == 200:
        root = BeautifulSoup(rs.content, 'html.parser')
        return root.select_one('div.user-details > a').text.strip()
    else:
        print("Ошибка: статус", rs.status_code)
        exit(-1)


urls = ['https://ru.stackoverflow.com/questions/962400', 'https://ru.stackoverflow.com/questions/962311', 'https://ru.stackoverflow.com/questions/962128', 'https://ru.stackoverflow.com/questions/962396', 'https://ru.stackoverflow.com/questions/962349']

t = time.time()
result = [go(url) for url in urls]
print(result)
print('Elapsed {:.3f} secs'.format(time.time() - t))
print()
# ['Streletz', 'Kromster', 'Stepan Kasyanenko', 'Kromster', 'JamesJGoodwin']
# Elapsed 6.030 secs

t = time.time()
pool = ThreadPool()
result = pool.map(go, urls)
print(result)
print('Elapsed {:.3f} secs'.format(time.time() - t))
print()
# ['Streletz', 'Kromster', 'Stepan Kasyanenko', 'Kromster', 'JamesJGoodwin']
# Elapsed 3.203 secs


###-------------------------Async-----------------------------------###


def go_async(text):
    urls = []
    root = BeautifulSoup(text, 'html.parser')
    result_asyncio.append(root.select_one('div.user-details > a').text.strip())
    return urls


async def request(client, url):
    global limit
    async with limit:
        async with client.get(url) as r:
            if(r.status == 200):
                return await r.text()



async def crawl(future, client, pool):
    futures = []
    urls_new = await future
    for request_future in asyncio.as_completed([request(client, url) for url in urls_new]):
        parse_future = loop.run_in_executor(pool, go_async, (await request_future))
        futures.append(asyncio.ensure_future(crawl(parse_future, client, pool)))
    if futures:
        await asyncio.wait(futures)

async def start_main(root_urls):
    loop = asyncio.get_event_loop()

    with ThreadPoolExecutor() as pool:
        async with aiohttp.ClientSession() as client:
            initial_future = loop.create_future()
            initial_future.set_result(root_urls)
            await crawl(initial_future, client, pool)

result_asyncio = []
t = time.time()
limit = asyncio.Semaphore(20)
loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(start_main(urls))
except KeyboardInterrupt:
    for task in asyncio.Task.all_tasks():
        task.cancel()
        with suppress(asyncio.CancelledError):
            loop.run_until_complete(task)
print(result_asyncio)
print('Elapsed {:.3f} secs'.format(time.time() - t))
print()

# ['Streletz', 'Kromster', 'Stepan Kasyanenko', 'Kromster', 'JamesJGoodwin']
# Elapsed 1.364
