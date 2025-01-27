# Use the official Python image as a base image
FROM python:3.11-slim

RUN apt-get update \
    && apt-get install -y firefox-esr \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir /root/Downloads

# Install Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && rm /tmp/requirements.txt

# Set the working directory
WORKDIR /app

# Copy your Selenium WebDriver script into the container
COPY unifibackup.py .

# Define the command to execute your script
ENTRYPOINT ["python", "unifibackup.py"]
