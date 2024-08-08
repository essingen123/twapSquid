import docker
import os
import pathlib
import sys

# Constants
SHARED_FOLDER_NAME = "shared"
TEST_NAMES = [f"test{i}_twap" for i in range(1, 5)]
DOCKERFILE_CONTENTS = """
FROM python:3.9-slim
RUN pip install pyppeteer
ENV PYPPETEER_EXECUTABLE_PATH=/usr/local/bin/chromium
WORKDIR /app
CMD ["python", "-m", "pyppeteer"]
"""

# URLs to test
URLS = [
    "https://news.ycombinator.com/",
    "https://example.com",
    "https://www.google.com",
    "https://www.python.org"
]

def create_test(test_name, url):
    """Create a test folder with a Dockerfile and main.py"""
    test_folder = pathlib.Path(test_name)
    test_folder.mkdir(exist_ok=True)
    (test_folder / "Dockerfile").write_text(DOCKERFILE_CONTENTS)
    (test_folder / "main.py").write_text(f"""
import asyncio
import pyppeteer

async def main():
    b = await pyppeteer.launch(headless=True, executablePath='/usr/local/bin/chromium')
    p = await b.newPage()
    await p.goto('{url!r}')
    await p.screenshot({{'path': '/shared/screenshot.png'}})
    await b.close()

asyncio.run(main())
""")

def main():
    """Run the tests"""
    client = docker.from_env()
    os.makedirs(SHARED_FOLDER_NAME, exist_ok=True)

    for test_name, url in zip(TEST_NAMES, URLS):
        create_test(test_name, url)
        image, _ = client.images.build(path=test_name, tag=f"{test_name}:latest")
        container = client.containers.run(
            f"{test_name}:latest",
            stdout=True,
            detach=False,
            volumes={os.path.join(os.getcwd(), SHARED_FOLDER_NAME): {'bind': '/shared','mode': 'rw'}}
        )
        container.stop()
        container.remove()

if __name__ == "__main__":
    if os.environ.get('TRACE_PRINTS_ENOUGH_THZ') == '1':
        import trace
        tracer = trace.Trace(count=False, trace=True)
        tracer.run('main()')
    else:
        main()
