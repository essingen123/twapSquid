import docker
import os
import pathlib

def create(test_name):
    (p:=pathlib.Path(test_name)).mkdir(exist_ok=True)
    return p

def build_and_run(client, test_name, url, shared_folder_name):
    test_folder = create(test_name)
    (test_folder/"Dockerfile").write_text(f"""
FROM python:3.9-slim
RUN pip install pyppeteer
ENV PYPPETEER_EXECUTABLE_PATH=/usr/local/bin/chromium
COPY download_chromium.py /app/download_chromium.py
RUN python /app/download_chromium.py
WORKDIR /app
COPY main.py /app/
CMD ["python", "main.py"]
""")
    (test_folder/"download_chromium.py").write_text("""
import pyppeteer;pyppeteer.chromium_downloader.download_chromium(overwrite=True, chromium_revision='857867')
""")
    (test_folder/"main.py").write_text(f"""
import asyncio;asyncio.run(async def main():(await (await pyppeteer.launch(headless=True, executablePath='/usr/local/bin/chromium')).newPage()).goto('{url!r}');(await (await (await pyppeteer.launch(headless=True, executablePath='/usr/local/bin/chromium')).newPage()).goto('{url!r}')).screenshot({{'path': '/shared/screenshot.png'}});await (await pyppeteer.launch(headless=True, executablePath='/usr/local/bin/chromium')).close())
""")
    image, _ = client.images.build(path=test_folder.absolute().as_posix(), tag=f"{test_name}:latest")
    return client.containers.run(f"{test_name}:latest", stdout=True, detach=False, volumes={os.path.join(os.getcwd(), shared_folder_name): {'bind': '/shared', 'mode': 'rw'}})

def main():
    client = docker.from_env()
    shared_folder_name = "shared"
    os.makedirs(shared_folder_name, exist_ok=True)
    test_names = [f"test{i}_twap" for i in range(1, 5)]
    urls = ["https://news.ycombinator.com/", "https://example.com", "https://www.google.com", "https://www.python.org"]
    containers = [build_and_run(client, test_name, url, shared_folder_name) for test_name, url in zip(test_names, urls)]
    for file in os.listdir(shared_folder_name):
        print(file)
    for container in containers:
        container.stop()
        container.remove()

if __name__ == "__main__":
    main()