
import pyppeteer
import os
import asyncio

async def main():
    try:
        browser = await pyppeteer.launch(headless=True, args=['--no-sandbox'])
        page = await browser.newPage()
        await page.goto('https://news.ycombinator.com/')
        await page.screenshot({"path": 'screenshot.png'})
        with open('test.txt', 'w') as f:
            f.write('Hello from Pyppeteer!')
        await browser.close()
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(main())
