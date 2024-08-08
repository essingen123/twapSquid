import docker
import os
import pathlib

def create_test_folder(test_name):
    test_folder = test_name
    if os.path.exists(test_folder):
        for file in os.listdir(test_folder):
            os.remove(os.path.join(test_folder, file))
    os.makedirs(test_folder, exist_ok=True)
    return test_folder

def create_dockerfile(test_folder):
    dockerfile = """
FROM python:3.9-slim
RUN pip install pyppeteer
RUN PYPPETEER_EXECUTABLE_PATH=/usr/local/bin/chromium python -c "import pyppeteer; import time; for i in range(3): try: pyppeteer.chromium_downloader.download_chromium(overwrite=True, chromium_revision='857867'); break; except Exception as e: print(f'Error downloading Chromium: {e}'); time.sleep(5);"
WORKDIR /app
COPY main.py /app/
CMD ["python", "main.py"]
"""
    dockerfile_path = pathlib.Path(test_folder) / "Dockerfile"
    dockerfile_path.write_text(dockerfile)

def create_main_py(test_folder):
    main_py = """
import asyncio
import pyppeteer

async def main():
  browser = await pyppeteer.launch(headless=True, executablePath='/usr/local/bin/chromium')
  page = await browser.newPage()
  await page.goto('https://news.ycombinator.com/')
  await page.screenshot({'path': '/shared/screenshot.png'})
  await browser.close()

asyncio.run(main())
"""
    main_py_path = pathlib.Path(test_folder) / "main.py"
    main_py_path.write_text(main_py)

def create_twapy_py(test_folder):
    twap_py = """
import os
import asyncio
import pyppeteer

async def main():
    os.environ["PYPPETEER_EXECUTABLE_PATH"] = "/usr/local/bin/chromium"
    browser = await pyppeteer.launch(headless=True, executablePath='/usr/local/bin/chromium')
    page = await browser.newPage()
    await page.goto("https://example.com")
    await page.screenshot({"path": "screenshot.png"})
    await browser.close()

asyncio.run(main())
"""
    twap_py_path = pathlib.Path(test_folder) / "twap.py"
    twap_py_path.write_text(twap_py)

def build_image(client, test_folder, test_name):
    image, _ = client.images.build(path=test_folder, tag=f"{test_name}:latest")
    return image

def run_container(client, test_name, shared_folder_name):
    container = client.containers.run(f"{test_name}:latest", stdout=True, detach=False, volumes={os.path.join(os.getcwd(), shared_folder_name): {'bind': '/shared','mode': 'rw'}})
    return container

def main():
    client = docker.from_env()
    shared_folder_name = "shared"
    os.makedirs(shared_folder_name, exist_ok=True)
    test_names = [f"test{i}_twap" for i in range(1, 9)]

    images = []
    for test_name in test_names:
        test_folder = create_test_folder(test_name)
        create_dockerfile(test_folder)
        create_main_py(test_folder)
        create_twapy_py(test_folder)
        image = build_image(client, test_folder, test_name)
        images.append(image)

    containers = []
    for test_name in test_names:
        container = run_container(client, test_name, shared_folder_name)
        containers.append(container)

    print("Screenshots taken:")
    for file in os.listdir(shared_folder_name):
        print(file)

    for container in containers:
        container.stop()
        container.remove()
    for image in images:
        client.images.remove(image.id)

if __name__ == "__main__":
    main()