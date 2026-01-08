FROM python:3.9-slim

# 1. Install system tools AND Tesseract OCR
RUN apt-get update && apt-get install -y wget gnupg2 unzip tesseract-ocr libtesseract-dev

# 2. Install Chrome safely
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get install -y ./google-chrome-stable_current_amd64.deb \
    && rm google-chrome-stable_current_amd64.deb \
    && apt-get clean

# 3. Setup App
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Start Server with 120 SECOND TIMEOUT
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000", "--timeout", "120"]
