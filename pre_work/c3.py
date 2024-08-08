import docker
import os
import pathlib
import time

# Create a Docker client
client = docker.from_env()

# Define the shared folder name
shared_folder_name = "shared"

# Create the shared folder
os.makedirs(shared_folder_name, exist_ok=True)

# Define the Docker image name
docker_image_name = "twap:latest"

# Define the test names
test_names = [f"test{i}_twap" for i in range(1, 9)]

# Create the Dockerfile
dockerfile = """
FROM python:3.9-slim
RUN pip install pyppeteer
WORKDIR /app
COPY main.py /app/
CMD ["python", "main.py"]
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
        for file in os.listdir(test_folder):
            os.remove(os.path.join(test_folder, file))
    os.makedirs(test_folder, exist_ok=True)

    # Create the Dockerfile and main.py files
    dockerfile_path = pathlib.Path(test_folder) / "Dockerfile"
    main_py_path = pathlib.Path(test_folder) / "main.py"
    dockerfile_path.write_text(dockerfile)
    main_py_path.write_text(main_py)

# Build the Docker images
images = []
for test_name in test_names:
    image, _ = client.images.build(path=test_name, tag=[f"{test_name}:latest"])
    images.append(image)

# Run the Docker containers
containers = []
for test_name in test_names:
    container = client.containers.run(f"{test_name}:latest", stdout=True, detach=True, volumes={os.path.join(os.getcwd(), shared_folder_name): {'bind': '/shared','mode': 'rw'}})
    containers.append(container)

# Wait for the containers to finish
for container in containers:
    while container.status!= 'exited':
        time.sleep(1)
        container.reload()

# Check if screenshots were taken
print("Screenshots taken:")
for file in os.listdir(shared_folder_name):
    print(file)

# Clean up
for container in containers:
    container.remove()
for image in images:
    client.images.remove(image.id)
