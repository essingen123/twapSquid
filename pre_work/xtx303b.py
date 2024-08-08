import docker
import os
import pathlib
import logging
import tempfile
import asyncio

logging.basicConfig(level=logging.DEBUG)

client = docker.from_env()

dockerfile = """FROM python:3.9-slim-buster
RUN retry=0; until [ $retry -ge 5 ]; do apt update && apt full-upgrade -y && apt install -y --no-install-recommends chromium-browser libgconf-2-4 && break || retry=$((retry+1)); done
RUN pip install pyppeteer
WORKDIR /app
CMD ["python", "-m", "pyppeteer"]"""

with tempfile.TemporaryDirectory() as tmpdir:
    with open(os.path.join(tmpdir, 'Dockerfile'), 'w') as f: f.write(dockerfile)
    image, _ = client.images.build(path=tmpdir, tag="twap:latest")

shared_folder = 'shared'
os.makedirs(shared_folder, exist_ok=True)
if not os.access(shared_folder, os.W_OK): exit(1)

script = """import pyppeteer; import os; import asyncio; async def main(): try: browser = await pyppeteer.launch(headless=True, args=['--no-sandbox']); page = await browser.newPage(); await page.goto('https://news.ycombinator.com/'); await page.screenshot({"path": 'screenshot.png'}); with open('test.txt', 'w') as f: f.write('Hello from Pyppeteer!'); await browser.close(); except Exception as e: print(f"Error: {e}"); asyncio.run(main())"""
with open('script.py', 'w') as f: f.write(script)

container = client.containers.run("twap:latest", stdout=True, detach=True, volumes={os.getcwd(): {'bind': '/app', 'mode': 'rw'}}, command="python script.py")

for line in container.logs(stream=True): print(line.decode())
container.wait(timeout=120)

print("Checking for test.txt file...")
print("Test.txt file found!" if os.path.exists(os.path.join(os.getcwd(), 'test.txt')) else "Test.txt file not found!")