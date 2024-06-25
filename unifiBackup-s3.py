import os
import logging
import shutil
import time
import boto3
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.options import Options

# Configure logging
logging.basicConfig(level=logging.INFO)

s3_client = boto3.client(
    's3',
    aws_access_key = os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name = os.getenv('AWS_REGION')
)

target_bucket = os.getenv("TARGET_BUCKET")

def load_environment_variables():
    username = os.getenv('USERNAME')
    password = os.getenv('PASSWORD')
    unifiip = os.getenv('UNIFI_IP')
    backupInterval = int(os.getenv('BACKUP_INTERVAL', '24'))  # default to 24 hours if not set
    output_directory = os.getenv('OUTPUT_DIRECTORY', os.path.expanduser('~/Downloads'))  # default to ~/Downloads if not set
    return username, password, unifiip, backupInterval, output_directory

def sleep_hours(hours):
    seconds = hours * 3600
    interval = 60  # sleep in 1-minute intervals
    while seconds > 0:
        time.sleep(min(interval, seconds))
        seconds -= interval

def setup_webdriver():
    options = Options()
    options.add_argument("--allow-running-insecure-content")
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options, service=FirefoxService(GeckoDriverManager().install()))
    return driver

def login_to_unifi(driver, username, password, unifiip):
    driver.get(f"https://{unifiip}")
    time.sleep(3)
    
    if username:
        username_field = driver.find_element(By.ID, 'login-username')
        logging.info("Username field found, entering username.")
        username_field.send_keys(username)
    else:
        logging.info("Username field not found. Skipping...")
    
    if password:
        password_field = driver.find_element(By.ID, 'login-password')
        logging.info("Password field found, entering password.")
        password_field.send_keys(password)
        time.sleep(1)
        password_field.submit()
        time.sleep(2)

def upload_to_s3(backup_file, key_name):
    s3_client.upload_file(Filename=backup_file, Bucket=target_bucket, Key=key_name)
    logging.info("File upload to S3 successfully")

def perform_backup(driver, output_directory):
    console_settings = driver.find_element(By.CSS_SELECTOR, '[data-testid="console-settings"]')
    logging.info("Found Console Settings.")
    console_settings.click()
    time.sleep(1)
    
    backup_button = driver.find_element(By.XPATH, '//span[contains(@class, "content__jTNy2Cxe") and text()="Back Up Now"]')
    logging.info("Backup field found, backing up now.")
    backup_button.click()
    logging.info("Waiting for backup to download...")
    time.sleep(30)
    
    # Ensure the output directory exists
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
        logging.info(f"Created output directory: {output_directory}")
    
    # Assume the most recent file in Downloads is the backup file
    downloads_path = os.path.expanduser('~/Downloads')
    latest_file = max([os.path.join(downloads_path, f) for f in os.listdir(downloads_path)], key=os.path.getctime)
    
    current_time = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
    new_file_name = f"unifi_os_backup_{current_time}.unifi"
    new_file_path = os.path.join(output_directory, new_file_name)
    
    shutil.move(latest_file, new_file_path)
    upload_to_s3(new_file_path, new_file_name)
    logging.info(f"Backup completed successfully. File saved as {new_file_path}")

def main():
    username, password, unifiip, backupInterval, output_directory = load_environment_variables()
    driver = setup_webdriver()
    
    try:
        while True:
            login_to_unifi(driver, username, password, unifiip)
            perform_backup(driver, output_directory)
            logging.info(f"Sleeping for {backupInterval} hours")
            sleep_hours(backupInterval)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
