# Use the official Python image as a base image
FROM python:3.11-slim

LABEL org.opencontainers.image.source="https://github.com/kwehen/UnifiBackup"

RUN apt-get update \
    && apt-get install -y firefox-esr \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && rm /tmp/requirements.txt

# Create the unifi user
RUN useradd -u 568 -m -d /home/unifi unifi

# Switch to the unifi user
USER unifi

# Create the Downloads directory under the unifi user's home directory
RUN mkdir -p /home/unifi/Downloads

# Set the working directory
WORKDIR /app

# Copy your Selenium WebDriver script into the container
COPY unifibackup.py .

# Define the command to execute your script
ENTRYPOINT ["python", "unifibackup.py"]
