FROM python:3.9-slim

# 1. Install dependencies
# We install wget and gnupg2 first to ensure they are available
RUN apt-get update && apt-get install -y wget gnupg2 unzip

# 2. Install Chrome directly (Bypassing apt-key issues)
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get install -y ./google-chrome-stable_current_amd64.deb \
    && rm google-chrome-stable_current_amd64.deb \
    && apt-get clean

# 3. Setup the App
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Run the App
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000"]
