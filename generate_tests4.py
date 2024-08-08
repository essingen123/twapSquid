import os
import time
import docker

# Define the test names
test_names = [f"test{i}_twap" for i in range(1, 9)]

# Define the shared folder name
shared_folder_name = "shared"

# Define the Docker image name
docker_image_name = "twap-ubuntu:latest"

# Define the log file name
log_file_name = "time_performance_log.txt"

# Create the shared folder
if not os.path.exists(shared_folder_name):
    print(f"Creating shared folder: {shared_folder_name}")
    os.makedirs(shared_folder_name)

# Function to create a test
def create_test(test_name):
    print(f"Creating test: {test_name}")

    # Create the test folder
    test_folder = test_name
    if os.path.exists(test_folder):
        print(f"Removing existing folder: {test_folder}")
        import shutil
        shutil.rmtree(test_folder)
    print(f"Creating folder: {test_folder}")
    os.makedirs(test_folder)

    # Create the Dockerfile
    print(f"Creating Dockerfile for {test_name}")
    with open(os.path.join(test_folder, "Dockerfile"), "w") as f:
        f.write("""
FROM ubuntu:latest
RUN apt update && apt install -y chromium-browser
COPY """ + test_name + """.py /app/
WORKDIR /app
CMD ["python", """ + test_name + """.py"]
""")

    # Create the script
    print(f"Creating script for {test_name}")
    with open(os.path.join(test_folder, test_name + ".py"), "w") as f:
        f.write("""
import time
from pyppeteer import launch

start_time = time.time()
browser = launch(headless=True, executablePath='/usr/bin/chromium-browser')
page = browser.newPage()
page.goto('https://news.ycombinator.com/')

# Save screenshot to /app/screenshot.png
page.screenshot({'path': '/app/screenshot.png'})

# Save screenshot to /shared/screenshot.png (original location)
page.screenshot({'path': '/shared/screenshot.png'})

end_time = time.time()
elapsed_time = end_time - start_time
print("Test completed in {:.2f} seconds".format(elapsed_time))
browser.close()

""")

    # Build the Docker image
    print(f"Building Docker image for {test_name}")
    client = docker.from_env()
    try:
        image, _ = client.images.build(path=test_folder, tag=docker_image_name)
        print(f"Docker image built successfully: {docker_image_name}")
    except docker.errors.BuildError as e:
        print(f"Error building Docker image: {str(e)}")

    # Run the Docker container
    print(f"Running Docker container for {test_name}")
    try:
        container = client.containers.run(docker_image_name, detach=True, volumes={os.path.join(os.getcwd(), shared_folder_name): {'bind': '/shared','mode': 'rw'}})
        print(f"Docker container running: {container.short_id}")
    except docker.errors.APIError as e:
        print(f"Error running Docker container: {str(e)}")

# Run the tests
for test_name in test_names:
    print(f"Starting test: {test_name}")
    start_time = time.time()
    create_test(test_name)
    end_time = time.time()
    elapsed_time = end_time - start_time
    with open(log_file_name, 'a') as f:
        f.write(f"{test_name}: {elapsed_time:.2f} seconds\n")
    print(f"Total time for {test_name}: {elapsed_time:.2f} seconds")
    print("------------------------")
