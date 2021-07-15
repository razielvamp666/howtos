import asyncio
from urllib.error import URLError
from urllib.request import urlopen
from awaits.awaitable import awaitable
from datetime import datetime as dt

urls = ['http://192.168.222.222', 'http://www.yandex.ru', 'http://www.google.com', 'http://bad_url_hgp9485gh875rghql45r7gelrufgbb.com', 'http://www.python.org']

print('\n ## ORDER ##\n')

i = 1
for url in urls:
  print(i,url)
  i += 1

# sync -> async conversion
# aiohttp may be used instead
# https://docs.aiohttp.org/en/stable/client_quickstart.html
@awaitable
def aurlopen(url):
    try:
        return urlopen(url).read()
    except URLError as e:
        return 'URL_ERROR'
    except ConnectionResetError:
        return 'CONNECTION_ERROR'

# get url data
async def print_head(url):
    print('Starting {} [{}]'.format(url, dt.now().strftime('%H:%M:%S')))
    data = await aurlopen(url)
    print('{}: {} bytes: {} [{}]'.format(url, len(data), data[0:50], dt.now().strftime('%H:%M:%S')))
    return '{}: {} bytes: {}'.format(url, len(data), data[0:50])

# run tasks
async def run_tasks(urls):
    results = []
    tasks = []

    for url in urls:
        tasks.append(asyncio.create_task(print_head(url)))

    for task in tasks:
        results.append(await task)

    print('\n -- In the end [' + dt.now().strftime('%H:%M:%S') + '] -- \n')

    for result in results:
        print(result)

print('\n ### FIRST WAY ### \n')

asyncio.run(run_tasks(urls))

print('\n ### SECOND WAY ### \n')

# after run asyncio.run main loop is closed so need to create new one
# https://docs.python.org/3/library/asyncio-eventloop.html
def get_or_create_eventloop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError as ex:
        if "There is no current event loop in thread" in str(ex):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return asyncio.get_event_loop()

tasks = [print_head(url) for url in urls]    
loop = get_or_create_eventloop()
results, _ = loop.run_until_complete(asyncio.wait(tasks))

print('\n -- In the end [' + dt.now().strftime('%H:%M:%S') + '] -- \n')

for result in results:
    print(result.result())

loop.close()
