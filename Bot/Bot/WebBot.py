import json
import threading
import time
from datetime import datetime
from telnetlib import EC
from selenium.webdriver.common.alert import Alert

import schedule
from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.support.wait import WebDriverWait

from API.getData import *
from Functions.WebFunction import *
from API.sendData import *
from configs.config import *
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from Resources.UserAgents import web_user_agents
from selenium.common.exceptions import NoSuchElementException

from solveRecaptcha.solveRecaptcha import solveRecaptcha

scheduled_orders = set()  # Set to keep track of scheduled orders



def is_recaptcha_present(driver):
    """
    :param driver: google driver
    :return: True if recaptcha popped up else False
    """
    try:
        time.sleep(3)
        # Check for the presence of reCAPTCHA iframe
        iframe = driver.find_element(By.XPATH, "//iframe[@title='reCAPTCHA']")
        print(iframe, "CAPTCHAA")
        print("captcha is here trying to solve it")
        result = solveRecaptcha(
            "6Le-wvkSAAAAAPBMRTvw0Q4Muexq9bi0DJwx_mJ-",
            driver.current_url
        )

        code = result['code']

        print(code)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'g-recaptcha-response'))
        )

        driver.execute_script(
            "document.getElementById('g-recaptcha-response').innerHTML = " + "'" + code + "'")

        time.sleep(5)
        submit_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[@type='submit'] | //input[@type='submit']"))
        )

        # Click the submit button
        submit_button.click()
        return True
    except NoSuchElementException:
        print("There is not captcha to solve!")
        return False


def setup_logging_for_order(order_id, domain):
    """Set up a separate logger for each order."""
    logger = logging.getLogger(str(order_id))  # Create a unique logger for the order
    logger.setLevel(logging.INFO)  # Set logging level

    # Ensure the logger has no handlers to prevent duplicate logs
    if not logger.handlers:
        # Check if the directory exists, if not, create it
        if not os.path.exists(LOGS):
            os.makedirs(LOGS)  # This creates the directory and any intermediate directories

        # Create a file handler specific to the order
        file_handler = logging.FileHandler(f'{LOGS}/logs.log')
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


mobile_emulation = {
    "deviceMetrics": {"width": 360, "height": 640, "pixelRatio": 3.0}
}


def start_google_search(driver, url, proxyusername, proxypassword):
    """
    When google is open, it starts a google search
    """
    parsed_url = urlparse(url)
    domain = parsed_url.netloc or parsed_url.path  # Handle URLs without a scheme

    # Prepare domain variations with and without 'www.'
    www_domain = f'www.{domain}' if not domain.startswith('www.') else domain
    non_www_domain = domain.replace('www.', '') if domain.startswith('www.') else domain

    # Navigate to Google and handle proxy auth
    driver.get("https://www.google.com")
    time.sleep(2)  # Wait for proxy auth dialog
    # Assuming pyautogui is handling proxy authentication as before
    pyautogui.typewrite(proxyusername)
    pyautogui.press('tab')
    pyautogui.typewrite(proxypassword)
    pyautogui.press('enter')

    driver.get("https://www.google.com")
    time.sleep(2)  # Ensure page loads

    search_input = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.NAME, "q"))
    )
    # Enter the domain in the search input
    for character in domain:
        search_input.send_keys(character)
        time.sleep(random.uniform(0.1, 0.5))  # Mimic human typing

    search_input.send_keys(Keys.RETURN)
    time.sleep(2)  # Wait for results to load

    # Check for sponsored results
    try:

        print("SPONSORED RESULTS: ")
        sponsored_results = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//span[text()='Sponsored']//ancestor::div[contains(@class, 'xpd')]"))
        )
        print("SPONSORED RESULTS: ", sponsored_results)
        for result in sponsored_results:
            link = result.find_element(By.TAG_NAME, "a")
            if any(domain in link.get_attribute("href") for domain in [www_domain, non_www_domain]):
                link.click()
                print("Clicked on a sponsored result.")
                return
    except Exception as e:
        print("No matching sponsored results or error occurred:", e)

    # If no sponsored result found, fall back to regular search results
    result_index = 1
    while True:
        print("NOT FOUND SPONSORED RESULTS")
        try:
            xpath = (f'//*[@id="rso"]/div[{result_index}]//a[contains(@href, "{www_domain}") or '
                     f'contains(@href, "{non_www_domain}")]')
            search_result = WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            search_result.click()
            print("Clicked on a regular search result.")
            break
        except Exception as e:
            print(f"Result {result_index} does not contain the domain {domain}.")
            result_index += 1
            if result_index > 10:  # Prevent infinite loop
                print("Reached the maximum search limit. URL not found.")
                break


def StartSEOBotWeb(ordersInfo, no, logger):
    randomProfileDjango = "http://" + DjangoURL + "/api/get/random/user/web/2"
    ProfileResponse = requests.get(randomProfileDjango)
    data = ProfileResponse.json()
    print("DATA: ", data)
    if 'error' in data:
        logger.error(f"Error fetching profile: {data['error']}")
        return
    id = ordersInfo.get("id", "")
    print("ID: ", id)
    try:
        url = ordersInfo.get("domain_name", "")
        proxy = ordersInfo.get("proxy", "")
        WorkTime = int(ordersInfo.get("work_sec", 0))
        match = re.search(r"www\.(.*)", url)
        text_after_www = match.group(1) if match else url
        scraping_process_complete(id)

        # Sanitize text_after_www to ensure it's a valid directory name
        # This step depends on your OS and its filesystem
        sanitized_text = re.sub(r'[\\/*?:"<>|]', "", text_after_www)  # Example for Windows

        profile_directory = os.path.join(os.getcwd(), f'Resources/Profiles/profile{data["id"]}')

        try:
            # Attempt to create the directory and catch any OSError
            os.makedirs(profile_directory, exist_ok=True)
        except OSError as e:
            print(f"Could not create directory {profile_directory}: {e}")
            return  # Stop execution if directory creation fails

        chrome_options = Options()

        chrome_options.add_argument(f"user-data-dir={profile_directory}")

        chrome_options.add_argument(f"--proxy-server={data['proxy']}")
        chrome_options.add_argument("--verbose")

        chrome_options.add_argument(f"user-agent={data['UserAgent']}")
        chrome_prefs = {
            "profile.default_content_setting_values.geolocation": 1,  # Allow geolocation
            "timezone": data["timezone"]
        }
        chrome_options.add_experimental_option("prefs", chrome_prefs)
        location = {
            "latitude": data["lat"],
            "longitude": data["long"],  # Ensure this is 'long' or 'lon' as per your data dictionary keys
            "accuracy": 100  # Set the location accuracy in meters
        }

        driver = None
        try:
            driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
            driver.execute_cdp_cmd("Emulation.setGeolocationOverride", location)

            driver.maximize_window()
            start_google_search(driver, url, data["proxyusername"], data["proxypassword"])
            time.sleep(2)
            start_time = time.time()
            while True:
                if is_recaptcha_present(driver):
                    print("captcha is here trying to solve-")
                    result = solveRecaptcha("6LfD3PIbAAAAAJs_eEHvoOl75_83eXSqpPSRFJ_u", driver.current_url)
                    code = result["code"]
                    print(code)

                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, 'g-recaptcha-response'))
                    )

                    driver.execute_script(
                        "document.getElementById('g-recaptcha-response').innerHTML = " + "'" + code + "'")

                    submit_button = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, "//button[@type='submit'] | //input[@type='submit']"))
                    )

                    submit_button.click()
                else:
                    pass
                if time.time() - start_time > WorkTime:
                    print("Reached the specified work time. Stopping.")
                    break
                # Ensure perform_random_action exists and is properly defined
                try:
                    center_mouse_and_scroll(driver, url, start_time, WorkTime)

                finally:
                    setProfileFree(data["id"])


        except Exception as e:
            setProfileFree(data["id"])
            scraping_process_incomplete(id)
            print(f"An error occurred: {e}")
        finally:
            if driver:
                setProfileFree(data["id"])
                driver.quit()

    except  OSError as e:
        print(f"Something Wrong while trying to start threads {no}")

        print(f"Error  {e}")


def process_order_web(order):
    order_id = order.get('id', 'Unknown')
    logger = setup_logging_for_order(order_id, order.get("domain_name", ""))  # Set up logging for this specific order

    start_time = time.time()
    logger.info(f"Starting processing order {order_id}.")
    StartSEOBotWeb(order, 1, logger)
    end_time = time.time()
    duration = end_time - start_time
    logger.info(f"Finished processing order {order_id}. Duration: {duration:.2f} seconds.")


def schedule_order_web(order):
    order_id = order['id']
    if order_id in scheduled_orders:
        print(f"Order {order_id} is already scheduled or processed.")
        return

    order_time = datetime.strptime(order['order_schedule'], "%Y-%m-%dT%H:%M:%SZ")
    current_time = datetime.utcnow()  # Assuming order_schedule is in UTC
    print(f"Current time {current_time}")
    if order_time <= current_time:
        # If the scheduled time has passed, process the order immediately
        print(f"Order {order_id} is past its schedule time and will be processed now.")
        process_order_web(order)
    else:
        # Schedule the order as its time has not yet passed
        schedule.every().day.at(order_time.strftime("%H:%M")).do(process_order_web, order=order)
        print(f"Scheduled order {order_id} for {order_time}")

    # Add the order_id to the set to prevent duplicate scheduling or processing
    scheduled_orders.add(order_id)


def BOTStartWeb(order_files):
    with open(order_files, 'r') as file:
        orders = json.load(file)
    schedule.run_pending()
    # Process each order sequentially, respecting max_workers for each
    for order in orders:
        if order['order_schedule'] is None:
            process_order_web(order)
        else:
            schedule_order_web(order)


def LoadBotWeb():
    while True:
        schedule.run_pending()

        try:
            fetch_orders_and_save_web()
        except:
            print("please check if there is any order")

        BOTStartWeb(ORDERS_LIST_Web_JSON)
