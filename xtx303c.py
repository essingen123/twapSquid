import docker
import os
import pathlib
import logging
import tempfile
import asyncio

logging.basicConfig(level=logging.DEBUG)

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

def create_docker_image():
    dockerfile = """FROM python:3.9-slim-buster
RUN retry=0; until [ $retry -ge 5 ]; do apt update && apt full-upgrade -y && apt install -y --no-install-recommends chromium-browser libgconf-2-4 && break || retry=$((retry+1)); done
RUN pip install pyppeteer
WORKDIR /app
CMD ["python", "-m", "pyppeteer"]"""
    with tempfile.TemporaryDirectory() as tmpdir:
        with open(os.path.join(tmpdir, 'Dockerfile'), 'w') as f:
            f.write(dockerfile)
        image, _ = client.images.build(path=tmpdir, tag="twap:latest")
        return image

def create_container(image):
    shared_folder = 'shared'
    os.makedirs(shared_folder, exist_ok=True)
    if not os.access(shared_folder, os.W_OK):
        exit(1)
    script = """import pyppeteer; import os; import asyncio;
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

asyncio.run(main())"""
    with open('script.py', 'w') as f:
        f.write(script)
    container = client.containers.run(image, stdout=True, detach=True, volumes={os.getcwd(): {'bind': '/app', 'mode': 'rw'}}, command="python script.py")
    return container

def check_test_file():
    print("Checking for test.txt file...")
    print("Test.txt file found!" if os.path.exists(os.path.join(os.getcwd(), 'test.txt')) else "Test.txt file not found!")

client = docker.from_env()
image = create_docker_image()
container = create_container(image)
for line in container.logs(stream=True):
    print(line.decode())
container.wait(timeout=120)
check_test_file()