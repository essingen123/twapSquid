import pyppeteer; import os; import asyncio;
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
        with open('folder2/test_write_text.txt', 'w') as f:
            f.write('Hello from Pyppeteer!')
        await b.close()

async def main():
    await lp()

asyncio.run(main())