from selenium import webdriver
import time
import os
# Path to the existing Chrome profile directory
# /Users/dev1/Desktop/Python Examples

script_dir = os.path.dirname(os.path.abspath(__file__))
folder_name = "profile_with_2captcha"
folder_path = os.path.join(script_dir, folder_name)
chrome_profile_directory = folder_path

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