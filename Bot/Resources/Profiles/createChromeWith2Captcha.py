from selenium import webdriver
import time
from Bot.configs.config import captcha_profile_dir
# Path to the existing Chrome profile directory
# /Users/dev1/Desktop/Python Examples
chrome_profile_directory = captcha_profile_dir

try:
    # Configure Chrome options to use the specified profile
    options = webdriver.ChromeOptions()
    options.add_argument(f"user-data-dir={chrome_profile_directory}")
    # Initialize the Chrome webdriver with the existing profile
    driver = webdriver.Chrome(options=options)

    # Example usage: navigate to a website
    driver.get("https://www.google.com")
    time.sleep(200)

    # Quit the browser and end the program
    driver.quit()

except Exception as e:
    print(f"Error occurred: {e}")