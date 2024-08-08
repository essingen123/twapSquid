# I want to make 8 diffrerent docker tests called 
# test1_twap.py
# test2_twap.py
# test3_twap.py
# etc
# 
# i want to make this with your help in max twenty minutes
# 
# the docker must be under 100 mb preferablyunder 60mb
# and run form start of docker to a screenshot in the shared folder in under 5 seconds 
# 
# this is a proof-of-concept code, terse almost golfed code is prefered
# ============================================================================
# Tiny Web Auto Pilot (TWAP) Project
# ----------------------------------------------------------------------------
# This script creates a lightweight Docker container for web automation tasks
# using Pyppeteer and a browser that can run in NON-HEADFUL mode. 
# It builds the Docker image,
# runs the container, navigates to a website, takes a screenshot, and logs the
# result to a file.
#
# The goal of this project is to create a fast and efficient web automation
# framework that can be used for various tasks, such as web scraping, testing,
# and monitoring.
#
# Author: kilian lindberg
# Date: 30241348
# ============================================================================
# 
import os
import time
import docker

folder_name = 'test1_twap'
shared_folder_name ='shared'
docker_image_name = 'twaper:latest'
log_file_name = 'time_performance_log.txt'

def create_folder(folder_name):
    if os.path.exists(folder_name):
        import shutil
        shutil.rmtree(folder_name)
    os.makedirs(folder_name)

def create_dockerfile(folder_name):
    with open(os.path.join(folder_name, 'Dockerfile'), 'w') as f:
        f.write('''
        FROM alpine:latest
        RUN apk add --no-cache chromium pyppeteer
        COPY test1_twap_orch.py /app/
        WORKDIR /app
        CMD ["python", "test1_twap_orch.py"]
        ''')

def create_script(folder_name):
    with open(os.path.join(folder_name, 'test1_twap_orch.py'), 'w') as f:
        f.write('''
        import time
        from pyppeteer import launch

        start_time = time.time()
        browser = launch(headless=True, executablePath='/usr/bin/chromium')
        page = browser.newPage()
        page.goto('https://news.ycombinator.com/')
        page.screenshot({'path': '/shared/screenshot.png'})
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Test completed in {elapsed_time:.2f} seconds")
        browser.close()
        ''')

def build_docker_image(folder_name, docker_image_name):
    client = docker.from_env()
    try:
        image, _ = client.images.build(path=folder_name, tag=docker_image_name)
        print(f"Docker image built successfully: {docker_image_name}")
    except docker.errors.BuildError as e:
        print(f"Error building Docker image: {e}")

def run_docker_container(docker_image_name, shared_folder_name):
    client = docker.from_env()
    try:
        container = client.containers.run(docker_image_name, detach=True, volumes={os.path.join(os.getcwd(), shared_folder_name): {'bind': '/shared','mode': 'rw'}})
        print(f"Docker container running: {container.short_id}")
    except docker.errors.APIError as e:
        print(f"Error running Docker container: {e}")

def main():
    start_time = time.time()
    create_folder(folder_name)
    create_folder(shared_folder_name)
    create_dockerfile(folder_name)
    create_script(folder_name)
    build_docker_image(folder_name, docker_image_name)
    run_docker_container(docker_image_name, shared_folder_name)
    end_time = time.time()
    elapsed_time = end_time - start_time
    with open(log_file_name, 'a') as