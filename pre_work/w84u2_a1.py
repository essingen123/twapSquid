import os

# Create Dockerfile
with open('Dockerfile', 'w') as f:
    f.write('FROM python:alpine\n'
            'RUN pip install pyppeteer\n'
            'RUN mkdir /app\n'
            'WORKDIR /app\n'
            'COPY . /app\n'
            'CMD ["python", "twap.py"]')

import os
# NOT FOR THE HOST HEY! # import asyncio # import pyppeteer

# Create twap.py
with open('twap.py', 'w') as f:
    f.write('import asyncio\n'
            'import pyppeteer\n'
            'async def main():\n'
            '    browser = await pyppeteer.launch(headless=True)\n'
            '    page = await browser.newPage()\n'
            '    await page.goto("https://example.com")\n'
            '    await page.screenshot({"path": "screenshot.png"})\n'
            '    await browser.close()\n'
            'asyncio.run(main())')

# Create test scripts
for i in range(1, 5):
    with open(f'test{i}_twap.py', 'w') as f:
        f.write('import os\n'
                f'os.system("docker build -t twap{i} .")\n'
                f'os.system(f"docker run -v {os.getcwd()}/shared:/shared twap{i} python twap.py")')

# Build and run Docker containers
for i in range(1, 5):
    os.system(f'docker build -t twap{i} .')
    os.system(f'docker run -v {os.getcwd()}/shared:/shared twap{i} python twap.py')