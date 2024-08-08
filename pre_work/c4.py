import docker
import os
import pathlib
import time

# Define constants
SHARED_FOLDER_NAME = "shared"
DOCKER_IMAGE_NAME = "twap:latest"
TEST_NAMES = [f"test{i}_twap" for i in range(1, 9)]

# Create a Docker client
client = docker.from_env()

def create_shared_folder():
    """Create the shared folder if it doesn't exist"""
    os.makedirs(SHARED_FOLDER_NAME, exist_ok=True)

def create_dockerfile_and_main_py(test_folder):
    """Create the Dockerfile and main.py files in the test folder"""
    dockerfile = """
    FROM python:3.9-slim
    RUN pip install pyppeteer
    WORKDIR /app
    COPY main.py /app/
    CMD ["python", "main.py"]
    """
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
    dockerfile_path = pathlib.Path(test_folder) / "Dockerfile"
    main_py_path = pathlib.Path(test_folder) / "main.py"
    dockerfile_path.write_text(dockerfile)
    main_py_path.write_text(main_py)

def build_docker_images(test_names):
    """Build the Docker images for each test"""
    images = []
    for test_name in test_names:
        image, _ = client.images.build(path=test_name, tag=f"{test_name}:latest")
        images.append(image)
    return images

def run_docker_containers(test_names):
    """Run the Docker containers for each test"""
    containers = []
    for test_name in test_names:
        container = client.containers.run(f"{test_name}:latest", stdout=True, detach=True, volumes={os.path.join(os.getcwd(), SHARED_FOLDER_NAME): {'bind': '/shared','mode': 'rw'}})
        containers.append(container)
    return containers

def wait_for_containers_to_finish(containers):
    """Wait for the containers to finish running"""
    for container in containers:
        while container.status!= 'exited':
            time.sleep(1)
            container.reload()

def check_screenshots(shared_folder_name):
    """Check if screenshots were taken"""
    print("Screenshots taken:")
    for file in os.listdir(shared_folder_name):
        print(file)

def clean_up(containers, images):
    """Clean up the containers and images"""
    for container in containers:
        container.remove()
    for image in images:
        client.images.remove(image.id)

def main():
    create_shared_folder()
    
    for test_name in TEST_NAMES:
        test_folder = test_name
        if os.path.exists(test_folder):
            for file in os.listdir(test_folder):
                os.remove(os.path.join(test_folder, file))
        os.makedirs(test_folder, exist_ok=True)
        create_dockerfile_and_main_py(test_folder)
    
    images = build_docker_images(TEST_NAMES)
    containers = run_docker_containers(TEST_NAMES)
    wait_for_containers_to_finish(containers)
    check_screenshots(SHARED_FOLDER_NAME)
    clean_up(containers, images)

if __name__ == "__main__":
    main()
