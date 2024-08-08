
FROM python:3.9-slim
RUN pip install pyppeteer
ENV PYPPETEER_EXECUTABLE_PATH=/usr/local/bin/chromium
WORKDIR /app
CMD ["python", "-m", "pyppeteer"]
