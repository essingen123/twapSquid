import docker as d
import os as o
import pathlib as p
import logging as l
import tempfile as t
import asyncio as a

l.basicConfig(level=l.DEBUG)

async def lp():
    try:
        b = await pp.launch(headless=True, args=['--no-sandbox'])
    except e:
        print(f"Error: {e}")
    else:
        p = await b.newPage()
        await p.goto('https://news.ycombinator.com/')
        await p.screenshot({"path": 'screenshot.png'})
        with open('test.txt', 'w') as f:
            f.write('Hello from Pyppeteer!')
        await b.close()

async def main():
    await lp()

def cdi():
    df = """FROM python:3.9-slim-buster
RUN retry=0; until [ $retry -ge 5 ]; do apt update && apt full-upgrade -y && apt install -y --no-install-recommends chromium-browser libgconf-2-4 && break || retry=$((retry+1)); done
RUN pip install pyppeteer
WORKDIR /app
CMD ["python", "-m", "pyppeteer"]"""
    with t.TemporaryDirectory() as td:
        with open(o.path.join(td, 'Dockerfile'), 'w') as f:
            f.write(df)
        i, _ = d.from_env().images.build(path=td, tag="twap:latest")
        return i

def cc(i):
    sf = 'shared'
    o.makedirs(sf, exist_ok=True)
    if not o.access(sf, o.W_OK):
        exit(1)
    folder2 = 'folder2'
    o.makedirs(folder2, exist_ok=True)
    if not o.access(folder2, o.W_OK):
        exit(1)
    chromium_download_path = o.path.join(folder2, 'chromium-download')
    if not o.path.exists(chromium_download_path):
        # Download Chromium only if it's not already present in the folder2 directory
        print("Downloading Chromium...")
        # Add the Chromium download code here
        print("Chromium download complete!")
    else:
        print("Chromium download already present in folder2 directory. Skipping download...")
    s = """import pyppeteer; import os; import asyncio;
async def lp():
    try:
        b = await pyppeteer.launch(headless=True, args=['--no-sandbox'])
    except e:
        print(f"Error: {e}")
    else:
        p = await b.newPage()
        await p.goto('https://news.ycombinator.com/')
        await p.screenshot({"path": 'screenshot.png'})
        with open('test.txt', 'w') as f:
            f.write('Hello from Pyppeteer!')
        await b.close()

async def main():
    await lp()

asyncio.run(main())"""
    with open('script.py', 'w') as f:
        f.write(s)
    c = d.from_env().containers.run(i, stdout=True, detach=True, volumes={o.getcwd(): {'bind': '/app', 'mode': 'rw'}, folder2: {'bind': '/folder2', 'mode': 'rw'}}, command="python script.py")
    return c

def ctf():
    print("Checking for test.txt file...")
    print("Test.txt file found!" if o.path.exists(o.path.join(o.getcwd(), 'test.txt')) else "Test.txt file not found!")

client = d.from_env()
i = cdi()
c = cc(i)
for l in c.logs(stream=True):
    print(l.decode())
c.wait(timeout=120)
ctf()