# Use the official Python image as a base image
FROM python:3.11-slim

RUN apt-get update \
    && apt-get install -y firefox-esr \
    && rm -rf /var/lib/apt/lists/*

RUN adduser -D -h /home/unifi -s /bin/sh unifi

# Install required packages
RUN pip install selenium
RUN pip install webdriver_manager
RUN pip install boto3

# Set the working directory
WORKDIR /app

# Copy your Selenium WebDriver script into the container
COPY unifibackup.py .
RUN chown -R unifi:unifi /app

USER unifi

# Define the command to execute your script
ENTRYPOINT ["python", "unifibackup.py"]
