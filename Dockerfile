FROM python:3.9-slim

# 1. FORCE PYTHON LOGS TO PRINT IMMEDIATELY
# This fixes the "Zero Process" issue where logs are hidden
ENV PYTHONUNBUFFERED=1

# 2. Install System Tools (Chrome + Tesseract OCR)
RUN apt-get update && apt-get install -y \
    wget \
    gnupg2 \
    unzip \
    tesseract-ocr \
    libtesseract-dev \
    && rm -rf /var/lib/apt/lists/*

# 3. Install Google Chrome Stable
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get install -y ./google-chrome-stable_current_amd64.deb \
    && rm google-chrome-stable_current_amd64.deb \
    && apt-get clean

# 4. Set Up Application
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

# 5. START SERVER (The "Nuclear" Command)
# --timeout 200: Gives the bot 3+ minutes (Fixes "Worker Timeout")
# --threads 4: Allows the bot to wait for websites without crashing the server
# --workers 1: Keeps it simple for the free tier
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000", "--timeout", "200", "--workers", "1", "--threads", "4"]
