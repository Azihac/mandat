FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y curl libnss3 libatk1.0-0 libatk-bridge2.0-0 libgtk-3-0 libx11-xcb1 libdrm2 libgbm1 libxcomposite1 libxrandr2 libasound2

RUN pip install playwright && playwright install --with-deps

COPY . .
EXPOSE 8000
CMD ["python", "app.py"]
