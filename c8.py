import docker
import os
import pathlib
import time
import tempfile
import subprocess

# Define constants
SHARED_FOLDER_NAME = "shared"
TEST_NAMES = [f"test{i}_twap" for i in range(1, 5)]

# Create a Docker client
client = docker.from_env()

# Create the shared folder
os.makedirs(SHARED_FOLDER_NAME, exist_ok=True)

# Define the Dockerfile contents
dockerfile_contents = """
FROM python:3.9-slim

RUN apt-get update && apt-get install -y chromium-browser --no-install-recommends

WORKDIR /app

CMD ["python", "-m", "pyppeteer"]
"""

# Create a temporary Dockerfile
with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_file:
    tmp_file.write(dockerfile_contents)
    dockerfile_path = tmp_file.name

# Define the test files
test_files = {
    "test1_twap.py": """
import pyppeteer

async def main():
    b = await pyppeteer.launch(headless=True, executablePath='/usr/bin/chromium-browser')
    p = await b.newPage()
    await p.goto('https://news.ycombinator.com/')
    await p.screenshot({'path': '/shared/screenshot1.png'})
    await b.close()

pyppeteer.run_until_complete(main())
""",
    "test2_twap.py": """
import pyppeteer

async def main():
    b = await pyppeteer.launch(headless=True, executablePath='/usr/bin/chromium-browser')
    p = await b.newPage()
    await p.goto('https://www.google.com/')
    await p.screenshot({'path': '/shared/screenshot2.png'})
    await b.close()

pyppeteer.run_until_complete(main())
""",
    "test3_twap.py": """
import pyppeteer

async def main():
    b = await pyppeteer.launch(headless=True, executablePath='/usr/bin/chromium-browser')
    p = await b.newPage()
    await p.goto('https://www.bing.com/')
    await p.screenshot({'path': '/shared/screenshot3.png'})
    await b.close()

pyppeteer.run_until_complete(main())
""",
    "test4_twap.py": """
import pyppeteer

async def main():
    b = await pyppeteer.launch(headless=True, executablePath='/usr/bin/chromium-browser')
    p = await b.newPage()
    await p.goto('https://www.duckduckgo.com/')
    await p.screenshot({'path': '/shared/screenshot4.png'})
    await b.close()

pyppeteer.run_until_complete(main())
""",
}

# Create the test files
for test_name, test_code in test_files.items():
    test_file_path = pathlib.Path(test_name)
    test_file_path.write_text(test_code)

# Build the Docker image
image, _ = client.images.build(path='.', dockerfile=dockerfile_path, tag="twap:latest")

# Remove the temporary Dockerfile
os.remove(dockerfile_path)

# Run the Docker containers
containers = []
for test_name in TEST_NAMES:
    container = client.containers.run("twap:latest", stdout=True, detach=True, volumes={os.path.join(os.getcwd(), SHARED_FOLDER_NAME): {'bind': '/shared','mode': 'rw'}}, command=f"python {test_name}.py")
    containers.append(container)

# Wait for the containers to finish
for container in containers:
    while container.status!= 'exited':
        time.sleep(1)
        container.reload()

# Check if screenshots were taken
print("Screenshots taken:")
for file in os.listdir(SHARED_FOLDER_NAME):
    print(file)

# Clean up
for container in containers:
    container.remove()
client.images.remove(image.id)

# Close the Docker client
client.close()

# Remove the shared folder
import shutil
shutil.rmtree(SHARED_FOLDER_NAME)

# Remove the test files
for test_name in test_files:
    os.remove(test_name)
