FROM python:3.9-slim

# Install Chrome and dependencies
RUN apt-get update && apt-get install -y wget gnupg unzip \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' \
    && apt-get update && apt-get install -y google-chrome-stable

# Set up the app
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

# Run the app
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000"]
