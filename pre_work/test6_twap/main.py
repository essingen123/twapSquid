
    import pyppeteer

    async def main():
      browser = await pyppeteer.launch(headless=True)
      page = await browser.newPage()
      await page.goto('https://news.ycombinator.com/')
      await page.screenshot({'path': '/shared/screenshot.png'})
      await browser.close()

    pyppeteer.run_until_complete(main())
    