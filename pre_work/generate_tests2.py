import os
import time
import docker

# Define the test names
test_names = [f"test{i}_twap" for i in range(1, 9)]

# Define the shared folder name
shared_folder_name = "shared"

# Define the Docker image name
docker_image_name = "twap:latest"

# Define the log file name
log_file_name = "time_performance_log.txt"

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
FROM busybox:latest
RUN opkg-install chromium
COPY """ + test_name + """.py /app/
WORKDIR /app
CMD ["python", """ + test_name + """.py"]
""")

    # Create the script
    with open(os.path.join(test_folder, test_name + ".py"), "w") as f:
        f.write("""
import time
from pyppeteer import launch

start_time = time.time()
browser = launch(headless=True, executablePath='/usr/bin/chromium')
page = browser.newPage()
page.goto('https://news.ycombinator.com/')
page.screenshot({'path': '/shared/""" + test_name + """.png'})
end_time = time.time()
elapsed_time = end_time - start_time
print("Test completed in {:.2f} seconds".format(elapsed_time))
browser.close()
""")

    # Build the Docker image
    client = docker.from_env()
    try:
        image, _ = client.images.build(path=test_folder, tag=docker_image_name)
        print("Docker image built successfully: " + docker_image_name)
    except docker.errors.BuildError as e:
        print("Error building Docker image: " + str(e))

    # Run the Docker container
    try:
        container = client.containers.run(docker_image_name, detach=True, volumes={os.path.join(os.getcwd(), shared_folder_name): {'bind': '/shared','mode': 'rw'}})
        print("Docker container running: " + container.short_id)
    except docker.errors.APIError as e:
        print("Error running Docker container: " + str(e))

# Run the tests
for test_name in test_names:
    start_time = time.time()
    create_test(test_name)
    end_time = time.time()
    elapsed_time = end_time - start_time
    with open(log_file_name, 'a') as f:
        f.write(str(int(time.time())) + " {:.2f} seconds\n".format(elapsed_time))
    print("Total time: {:.2f} seconds".format(elapsed_time))
