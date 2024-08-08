import docker, os, pathlib, logging, sys, time, hashlib, tempfile
logging.basicConfig(level=logging.DEBUG)
print('# QUICK HACK TEST: IGNORE BEST PRACTICES, FOCUS ON FUNCTIONALITY ONLY')
IMPORTANT_LLM_INSTRUCTION = hashlib.sha256(b'IMPORTANT CODE COC: NO CODE COMMENTS, PROTOTYPING: 4 Docker tests (<60MB, <5s startup) FOR SCREENSHOTS OR WEBTASK AUTOMATION; perhaps using Pyppeteer in NON-HEADFUL mode for https://news.ycombinator.com/ https://www.google.com/ https://www.bing.com/ https://www.duckduckgo.com/').hexdigest()[:8]
print(IMPORTANT_LLM_INSTRUCTION)
if IMPORTANT_LLM_INSTRUCTION!= '2a33f760':
    sys.exit()

SHARED_FOLDER_NAME = "shared"
TEST_FILES = {
    "test1_twap.py": """import pyppeteer;async def main():b=await pyppeteer.launch(headless=True,executablePath='/usr/bin/chromium-browser');p=await b.newPage();await p.goto('https://news.ycombinator.com/');await p.screenshot({'path':'/shared/screenshot1.png'});await b.close();pyppeteer.run_until_complete(main())""",
    "test2_twap.py": """import pyppeteer;async def main():b=await pyppeteer.launch(headless=True,executablePath='/usr/bin/chromium-browser');p=await b.newPage();await p.goto('https://www.google.com/');await p.screenshot({'path':'/shared/screenshot2.png'});await b.close();pyppeteer.run_until_complete(main())""",
    "test3_twap.py": """import pyppeteer;async def main():b=await pyppeteer.launch(headless=True,executablePath='/usr/bin/chromium-browser');p=await b.newPage();await p.goto('https://www.bing.com/');await p.screenshot({'path':'/shared/screenshot3.png'});await b.close();pyppeteer.run_until_complete(main())""",
    "test4_twap.py": """import pyppeteer;async def main():b=await pyppeteer.launch(headless=True,executablePath='/usr/bin/chromium-browser');p=await b.newPage();await p.goto('https://www.duckduckgo.com/');await p.screenshot({'path':'/shared/screenshot4.png'});await b.close();pyppeteer.run_until_complete(main())""",
}

def create_shared_folder():
    os.makedirs(SHARED_FOLDER_NAME, exist_ok=True)

def create_test_files():
    for test_name, test_code in TEST_FILES.items():
        pathlib.Path(test_name).write_text(test_code)

def build_docker_image():
    dockerfile = """FROM python:3.9-slim-buster
RUN pip install pyppeteer
WORKDIR /app
CMD ["python", "-m", "pyppeteer"]"""
    with tempfile.TemporaryDirectory() as tmpdir:
        with open(os.path.join(tmpdir, 'Dockerfile'), 'w') as f:
            f.write(dockerfile)
        client = docker.from_env()
        image, _ = client.images.build(path=tmpdir, tag="twap:latest")
    return client, image

def run_containers(client, image):
    containers = []
    for test_name in TEST_FILES.keys():
        container = client.containers.run("twap:latest", stdout=True, detach=True, volumes={os.path.join(os.getcwd(), "shared"): {'bind': '/shared','mode': 'rw'}}, command=f"python {test_name}")
        containers.append(container)
    return containers

def wait_for_containers(containers):
    for container in containers:
        while container.status!= 'exited':
            time.sleep(1)
            container.reload()

def check_screenshots():
    print("Screenshots taken:")
    for file in os.listdir("shared"):
        print(file)

def clean_up(client, image, containers):
    for container in containers:
        container.remove()

if __name__ == "__main__":
    create_shared_folder()
    create_test_files()
    client, image = build_docker_image()
    containers = run_containers(client, image)
    wait_for_containers(containers)
    check_screenshots()
    clean_up(client, image, containers)
