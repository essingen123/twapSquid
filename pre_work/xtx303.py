import docker
import os
import pathlib
import logging
import tempfile
import asyncio

logging.basicConfig(level=logging.DEBUG)

# Create a Docker client
client = docker.from_env()

# Create a Dockerfile for the Pyppeteer image
dockerfile = """
FROM python:3.9-slim-buster
RUN retry=0; \
until [ $retry -ge 5 ]; do \
    apt update && apt full-upgrade -y && apt install -y --no-install-recommends chromium-browser libgconf-2-4 && break || retry=$((retry+1)); \
done
RUN pip install pyppeteer
WORKDIR /app
CMD ["python", "-m", "pyppeteer"]
"""

# Create a temporary directory for the Docker build context
with tempfile.TemporaryDirectory() as tmpdir:
    # Write the Dockerfile to the temporary directory
    with open(os.path.join(tmpdir, 'Dockerfile'), 'w') as f:
        f.write(dockerfile)

    # Build the Docker image
    image, _ = client.images.build(path=tmpdir, tag="twap:latest")

# Create a shared folder for the output
shared_folder = 'shared'
if not os.path.exists(shared_folder):
    os.makedirs(shared_folder, exist_ok=True)

# Check if the current user has write permission to the folder
if not os.access(shared_folder, os.W_OK):
    print(f"Error: No write permission to folder {shared_folder}")
    exit(1)

# Create a Pyppeteer script that outputs a test.txt file
script = """
import pyppeteer
import os
import asyncio

async def main():
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

asyncio.run(main())
"""

# Write the script to a file
with open('script.py', 'w') as f:
    f.write(script)

# Run the Docker container with the script and shared folder
container = client.containers.run("twap:latest", stdout=True, detach=True, volumes={os.getcwd(): {'bind': '/app', 'mode': 'rw'}}, command=f"python script.py")

# Stream the container logs to the terminal
for line in container.logs(stream=True):
    print(line.decode())

# Wait for the container to finish
container.wait(timeout=120)

# Check if the test.txt file was created
print("Checking for test.txt file...")
if os.path.exists(os.path.join(os.getcwd(), 'test.txt')):
    print("Test.txt file found!")
else:
    print("Test.txt file not found!")