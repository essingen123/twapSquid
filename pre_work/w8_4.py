import docker
import os
import pathlib

def create(test_name):
    test_folder = pathlib.Path(test_name)
    test_folder.mkdir(exist_ok=True)
    return test_folder

def create_dockerfile(test_folder):
    (test_folder / "Dockerfile").write_text("""
FROM python:3.9-slim
RUN pip install pyppeteer
RUN PYPPETEER_EXECUTABLE_PATH=/usr/local/bin/chromium python -c "import pyppeteer; import time; for i in range(3): try: pyppeteer.chromium_downloader.download_chromium(overwrite=True, chromium_revision='857867'); break; except Exception as e: print(f'Error downloading Chromium: {e}'); time.sleep(5);"
WORKDIR /app
COPY main.py /app/
CMD ["python", "main.py"]
""")

def create_main_py(test_folder, url):
    (test_folder / "main.py").write_text(f"""
import asyncio
import pyppeteer

async def main():
  browser = await pyppeteer.launch(headless=True, executablePath='/usr/local/bin/chromium')
  page = await browser.newPage()
  await page.goto('{url}')
  await page.screenshot({'path': '/shared/screenshot.png'})
  await browser.close()

asyncio.run(main())
""")

def build_and_run(client, test_name, url, shared_folder_name):
    test_folder = create_test(test_name)
    create_dockerfile(test_folder)
    create_main_py(test_folder, url)
    image, _ = client.images.build(path=test_folder, tag=f"{test_name}:latest")
    container = client.containers.run(f"{test_name}:latest", stdout=True, detach=False, volumes={os.path.join(os.getcwd(), shared_folder_name): {'bind': '/shared', 'mode': 'rw'}})
    return container

def main():
    client = docker.from_env()
    shared_folder_name = "shared"
    os.makedirs(shared_folder_name, exist_ok=True)
    test_names = [f"test{i}_twap" for i in range(1, 5)]
    urls = ["https://news.ycombinator.com/", "https://example.com", "https://www.google.com", "https://www.python.org"]

    containers = [build_and_run(client, test_name, url, shared_folder_name) for test_name, url in zip(test_names, urls)]

    print("Screenshots taken:")
    for file in os.listdir(shared_folder_name):
        print(file)

    for container in containers:
        container.stop()
        container.remove()

if __name__ == "__main__":
    main()