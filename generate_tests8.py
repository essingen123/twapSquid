import os
import time
import docker

# Define the test names
test_names = [f"test{i}_twap" for i in range(1, 9)]

# Define the shared folder name
shared_folder_name = "shared"

# Define the Docker image name
docker_image_name = "twap-ubuntu:latest"

# Create a Docker client
client = docker.from_env()

# Create the shared folder
if not os.path.exists(shared_folder_name):
    os.makedirs(shared_folder_name)

# Function to create a test
def create_test(test_name):
    # Create the test folder
    test_folder = test_name
    if os.path.exists(test_folder):
        import shutil
        shutil.rmtree(test_folder)
    os.makedirs(test_folder)

    # Create the Dockerfile
    with open(os.path.join(test_folder, "Dockerfile"), "w") as f:
        f.write("""
        FROM ubuntu:latest
        RUN apt update && apt install -y chromium-browser python3-pip
        COPY requirements.txt /app/
        WORKDIR /app
        RUN pip3 install -r requirements.txt
        COPY """ + test_name + """.py /app/
        CMD ["python3", """ + test_name + """.py"]
        """)

    # Create the requirements file
    with open(os.path.join(test_folder, "requirements.txt"), "w") as f:
        f.write("pyppeteer")

    # Create the test script
    with open(os.path.join(test_folder, test_name + ".py"), "w") as f:
        f.write("""
import time
from pyppeteer import launch

start_time = time.time()
browser = launch(headless=True, executablePath='/usr/bin/chromium-browser')
page = browser.newPage()
page.goto('https://news.ycombinator.com/')
page.screenshot({'path': '/shared/screenshot.png'})
browser.close()
print("Test completed in {:.2f} seconds".format(time.time() - start_time))
""")

    # Build the Docker image
    try:
        image, build_log = client.images.build(path=test_folder, tag=docker_image_name)
        for line in build_log:
            if'stream' in line:
                            print(line['stream'].strip())
            elif 'error' in line:
                print(f"Error: {line['error']}")
                raise Exception(f"Error building Docker image: {line['error']}")
    except docker.errors.BuildError as e:
        print(f"Error building Docker image: {e}")
        return None

    # Run the Docker container
    try:
        container = client.containers.run(docker_image_name, detach=True, volumes={os.path.join(os.getcwd(), shared_folder_name): {'bind': '/shared','mode': 'rw'}})
        return container
    except docker.errors.APIError as e:
        print(f"Error running Docker container: {e}")
        return None

# Run the tests
for test_name in test_names:
    print(f"Starting test: {test_name}")
    start_time = time.time()
    container = create_test(test_name)
    if container is None:
        print(f"Test {test_name} failed to start")
        continue
    for line in container.logs(stdout=True, stderr=True, stream=True):
        print(line.decode('utf-8').strip())
    end_time = time.time()
    print(f"Test completed in {end_time - start_time:.2f} seconds")
    print("------------------------")
