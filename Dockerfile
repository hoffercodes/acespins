# FIX: Use the FULL Python image (Debian based) instead of 'slim'
# This fixes the "Unmet dependencies" error by including standard Linux libraries.
FROM python:3.9

# 1. FORCE LOGS
ENV PYTHONUNBUFFERED=1

# 2. Install Tools & Tesseract
RUN apt-get update && apt-get install -y \
    wget \
    gnupg2 \
    unzip \
    tesseract-ocr \
    libtesseract-dev \
    # Explicitly install Chrome dependencies to be 100% safe
    fonts-liberation \
    libasound2 \
    libgbm1 \
    libnspr4 \
    libnss3 \
    xdg-utils

# 3. Install Google Chrome
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get install -y ./google-chrome-stable_current_amd64.deb \
    && rm google-chrome-stable_current_amd64.deb \
    && apt-get clean

# 4. Setup App
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

# 5. START SERVER (Hardcoded 200s limit)
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000", "--timeout", "200", "--workers", "1", "--threads", "4"]
