# Tiny Web Auto Pilot (TWAP) Project: 4 Docker tests (<60MB, <5s startup) using Pyppeteer in NON-HEADFUL mode, authored by Kilian Lindberg on 30241348, with a max dev time of 20 minutes (human + LLM) for a prototype-speed-coding fast-hack, prioritizing golfed code.

import docker
import os
import pathlib

SHARED_FOLDER_NAME = "shared"
TEST_NAMES = [f"test{i}_twap" for i in range(1, 5)]
DOCKERFILE_CONTENTS = """
FROM python:3.9-slim
RUN pip install pyppeteer
ENV PYPPETEER_EXECUTABLE_PATH=/usr/local/bin/chromium
WORKDIR /app
CMD ["python", "-m", "pyppeteer"]
"""

URLS = [
    "https://news.ycombinator.com/",
    "https://example.com",
    "https://www.google.com",
    "https://www.python.org"
]

def create_test(test_name, url):
    test_folder = pathlib.Path(test_name)
    test_folder.mkdir(exist_ok=True)
    (test_folder / "Dockerfile").write_text(DOCKERFILE_CONTENTS)
    (test_folder / "main.py").write_text(f"""
import asyncio
import pyppeteer
async def main():
    b = await pyppeteer.launch(headless=True)
    p = await b.newPage()
    await p.goto('{url!r}')
    await p.screenshot({{'path': '/shared/screenshot.png'}})
    await b.close()
asyncio.run(main())
""")

def main():
    client = docker.from_env()
    os.makedirs(SHARED_FOLDER_NAME, exist_ok=True)
    for test_name, url in zip(TEST_NAMES, URLS):
        create_test(test_name, url)
        image, _ = client.images.build(path=test_name, tag=f"{test_name}:latest")
        client.containers.run(f"{test_name}:latest", volumes={os.path.join(os.getcwd(), SHARED_FOLDER_NAME): {'bind': '/shared','mode': 'rw'}})

if __name__ == "__main__":
    main()
