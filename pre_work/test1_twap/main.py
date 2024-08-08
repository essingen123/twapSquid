
import asyncio
import pyppeteer

async def main():
    b = await pyppeteer.launch(headless=True, executablePath='/usr/local/bin/chromium')
    p = await b.newPage()
    await p.goto(''https://news.ycombinator.com/'')
    await p.screenshot({'path': '/shared/screenshot.png'})
    await b.close()

asyncio.run(main())
