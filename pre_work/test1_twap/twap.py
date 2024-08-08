
import os
import asyncio
import pyppeteer

async def main():
    os.environ["PYPPETEER_EXECUTABLE_PATH"] = "/usr/local/bin/chromium"
    browser = await pyppeteer.launch(headless=True, executablePath='/usr/local/bin/chromium')
    page = await browser.newPage()
    await page.goto("https://example.com")
    await page.screenshot({"path": "screenshot.png"})
    await browser.close()

asyncio.run(main())
