import docker
import os

# Create a Docker client
client = docker.from_env()

# Define the shared folder name
shared_folder_name = "shared"

# Create the shared folder
if not os.path.exists(shared_folder_name):
    os.makedirs(shared_folder_name)

# Define the Docker image name
docker_image_name = "twap:latest"

# Define the test names
test_names = [f"test{i}_twap" for i in range(1, 9)]

# Create the Dockerfile
dockerfile = """
FROM python:3.9-slim
RUN pip install pyppeteer
COPY. /app
WORKDIR /app
CMD ["python", "-m", "pyppeteer"]
"""

# Create the main.py file
main_py = """
import pyppeteer

async def main():
  browser = await pyppeteer.launch(headless=True)
  page = await browser.newPage()
  await page.goto('https://news.ycombinator.com/')
  await page.screenshot({'path': '/shared/screenshot.png'})
  await browser.close()

pyppeteer.run_until_complete(main())
"""

# Create the tests
for test_name in test_names:
    # Create the test folder
    test_folder = test_name
    if os.path.exists(test_folder):
        import shutil
        shutil.rmtree(test_folder)
    os.makedirs(test_folder)

    # Create the Dockerfile and main.py files
    with open(os.path.join(test_folder, "Dockerfile"), "w") as f:
        f.write(dockerfile)
    with open(os.path.join(test_folder, "main.py"), "w") as f:
        f.write(main_py)

    # Build the Docker image
    image, _ = client.images.build(path=test_folder, tag=f"{test_name}:latest")

    # Run the Docker container
    container = client.containers.run(f"{test_name}:latest", detach=True, volumes={os.path.join(os.getcwd(), shared_folder_name): {'bind': '/shared','mode': 'rw'}}, command="python main.py")
