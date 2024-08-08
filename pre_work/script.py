import pyppeteer; import os; import asyncio;
async def launch_pyppeteer():
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

async def main():
    await launch_pyppeteer()

asyncio.run(main())