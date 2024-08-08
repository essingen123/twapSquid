
import pyppeteer
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--output", help="output file path")
args = parser.parse_args()

async def main():
    browser = await pyppeteer.launch(headless=True, executablePath='/usr/bin/chromium-browser')
    page = await browser.newPage()
    await page.goto('https://www.google.com/')
    await page.screenshot({"path": args.output})
    await browser.close()

pyppeteer.run_until_complete(main())
