import asyncio
import pyppeteer
async def main():
    browser = await pyppeteer.launch(headless=True)
    page = await browser.newPage()
    await page.goto("https://example.com")
    await page.screenshot({"path": "screenshot.png"})
    await browser.close()
asyncio.run(main())