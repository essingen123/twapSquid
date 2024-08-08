FROM python:3.9-slim
RUN apt-get update && apt-get install -y chromium-browser --no-install-recommends
WORKDIR /app
CMD ["python", "-m", "pyppeteer"]