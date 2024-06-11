from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

import time
import pyautogui
import random
import sys
import os
from urllib.parse import urlparse
import requests
import shutil
import threading
import zipfile

# from solveRecaptcha.solveRecaptcha import solveRecaptcha
# from telnetlib import EC

# from API.getData import *
# from Functions.WebFunction import *
# from API.sendData import *

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from configs.config import *




used_profiles = []

class Bot:
    def __init__(self):

        self.django_url = DjangoURL
        self.driver = None
        self.url = ""
        
        self.chrome_options = None 
        self.location = None
        self.profile_dir = None
        self.profile_in_use = False

        self.mobile_emulation = {
            "deviceMetrics": {"width": 360, "height": 640, "pixelRatio": 3.0}
        }

        self.parsed_url = ""
        self.domain = ""
        self.profile = {}
        self.order = {}

        self.result_to_click = None
        self.sponsored_results = []
        self.business_results = {'parent': [], 'results': []}
        self.location_results = {'parent': [], 'results': []}
        self.sponsored_business_results = {'parent': [], 'results': []}

        self.location_or_business = 'Location'

        self.xpaths = {
            'Sponsored' : "//span[text()='Sponsored']//ancestor::div[contains(@class, 'xpd')]",
            'Location': {
                'parent': '//*[@id="Odp5De"]/div/div/div[1]/div[2]',
                'elements_template': '//*[contains(@id, "tsuid_")]//a[@role="button" and contains(@class, "vwVdIc")]',
                'first_element': '//*[@id="Odp5De"]/div/div/div[1]/div[2]/div[1]/div/div[2]/div[1]/div/div[1]',#//*[@id="tsuid_144"] 
                'second_element': '//*[@id="Odp5De"]/div/div/div[1]/div[2]/div[1]/div/div[2]/div[1]/div/div[2]',#//*[@id="tsuid_145"]
                'third_element': '//*[@id="Odp5De"]/div/div/div[1]/div[2]/div[1]/div/div[2]/div[1]/div/div[3]',#//*[@id="tsuid_146"]
                'buttons': 'bkaPDb',
            },
            'Business': {
                'parent': '//*[@id="rso"]/div[7]/div/div/div[1]/div[4]',
                'elements_template': '//*[contains(@id, "tsuid_")]//a[@role="link"]',
                'elements': "//div[@class='uMdZh tIxNaf rllt__borderless']//a[@role='link']", 
                'buttons': 'in2fcf', 
            },
            'Sponsored business': {
                'parent': "//div[@id='taw']",
                'elements_template': "(//div[@class='ixr6Zb ylJcKd RX9eSe'])",
                'buttons': '',
            }
        }

        self.manifest_json = """
            {
                "version": "1.0.0",
                "manifest_version": 2,
                "name": "Chrome Proxy",
                "permissions": [
                    "proxy",
                    "tabs",
                    "unlimitedStorage",
                    "storage",
                    "<all_urls>",
                    "webRequest",
                    "webRequestBlocking"
                ],
                "background": {
                    "scripts": ["background.js"]
                },
                "minimum_chrome_version":"22.0.0"
            }
            """
        self.background_js = None
        
    def set_plugin_for_proxy(self):
        """
        Sets Background js used in proxy
        """
        self.set_proxy()
        PROXY_HOST = self.profile['proxy'].split('@')[1].split(':')[0]
        PROXY_PORT = self.profile['proxy'].split('@')[1].split(':')[1]
        PROXY_USER = self.profile['proxy'].split('@')[0].split('//')[1].split(':')[0]
        PROXY_PASS = self.profile['proxy'].split('@')[0].split('//')[1].split(':')[1]
        self.background_js = """
                            var config = {
                                        mode: "fixed_servers",
                                        rules: {
                                        singleProxy: {
                                            scheme: "http",
                                            host: "%s",
                                            port: parseInt(%s)
                                        },
                                        bypassList: ["localhost"]
                                        }
                                    };

                                chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

                                function callbackFn(details) {
                                    return {
                                        authCredentials: {
                                            username: "%s",
                                            password: "%s"
                                        }
                                    };
                                }

                                chrome.webRequest.onAuthRequired.addListener(
                                            callbackFn,
                                            {urls: ["<all_urls>"]},
                                            ['blocking']
                                );
                                """ % (PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS)
        
        pluginfile = 'proxy_auth_plugin.zip'
        with zipfile.ZipFile(pluginfile, 'w') as zp:
            zp.writestr("manifest.json", self.manifest_json)
            zp.writestr("background.js", self.background_js)
        return pluginfile

    
    
    def __is_recaptcha_present(self):
        """
        Checks if there is a recaptcha
        """
        print("Checking if there is a recaptcha")
        try:
            time.sleep(3)
            iframe = self.driver.find_element(By.XPATH, "//iframe[@title='reCAPTCHA']")
            return True
        except Exception as e:
            print("Captcha not found")
            return False

    def solve_captcha(self):

        if self.__is_recaptcha_present():
            print("Solving Captcha")
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="recaptcha"]/div/div[2]'))
            ).click()
            try:
                WebDriverWait(self.driver, 100).until(EC.text_to_be_present_in_element((By.XPATH, '//*[@id="recaptcha"]/div/div[2]'), "Captcha solved"))
                time.sleep(2)
                print("Captcha solved!")
            except Exception as e:
                if self.__is_recaptcha_present():
                    print("Error solving captcha: ", e)
                    self.close_web_driver()
                pass
            
    def set_proxy(self):

        """
        Fixes proxy for authentication
        :return:
        """
        self.__proxy = f"http://{self.profile['proxyusername']}:{self.profile['proxypassword']}@{self.profile['proxy']}"
        self.profile['proxy'] = self.__proxy

    def authenticate_proxy(self):

        """
        passes the authentication of proxy when starting webbrowser
        :return:
        """
        self.driver.get("https://www.google.com")
        pyautogui.write(self.profile['proxyusername'])
        pyautogui.press('tab')
        pyautogui.write(self.profile['proxypassword'])
        pyautogui.press('enter')
        self.driver.get("https://www.google.com")
    def __create_new_profile_dir_from_existing_profile(self):
        """
        Copies main profile directory with 2captcha installed on it into a new profile directory
        """
        from pathlib import Path
        parent_dir = Path(__file__).parent
        main_profile_dir = parent_dir.parent / 'resources' / 'profiles' / 'profile_with_2captcha'

        if not os.path.exists(self.profile_dir):
            shutil.copytree(main_profile_dir, self.profile_dir)
            print(f'{self.profile_dir} created')
        


    def set_or_create_profile_directory(self):
        """
        Creates profile directory if this profile directory does not exist, else does not create directory
        if it catches OS Error, logs the reason why didnt it do its job.
        """
        self.profile_dir = os.path.join(os.getcwd(), f'Resources/Profiles/profile{self.profile["id"]}')
        try:
            self.__create_new_profile_dir_from_existing_profile()
        except OSError as e:
            print(f"Could not create directory {self.profile_dir}: {e}")
            return 

    def set_location(self):
        """Sets the location according to profile fetched"""
        self.location = {
            "latitude": self.profile["lat"],
            "longitude": self.profile["long"],  # Ensure this is 'long' or 'lon' as per your data dictionary keys
            "accuracy": 100  # Set the location accuracy in meters
        }
        self.driver.execute_cdp_cmd("Emulation.setGeolocationOverride", self.location)


    def set_chrome_options(self):
        """
        Configures chrome options
        """
        self.chrome_options = Options()
        self.chrome_options.add_argument(f"user-data-dir={self.profile_dir}")
        plugin_file = self.set_plugin_for_proxy()
        self.chrome_options.add_extension(plugin_file)
        # self.chrome_options.add_argument(f"proxy-server={self.profile['proxy']}")
        # self.chrome_options.add_argument(f"--proxy={self.proxy}")
        self.chrome_options.add_argument("--verbose")
        self.chrome_options.add_argument(f"user-agent={self.profile['UserAgent']}")

        chrome_prefs = {
            "profile.default_content_setting_values.geolocation": 1,  # Allow geolocation
            "timezone": self.profile["timezone"]
        }
        self.chrome_options.add_experimental_option("prefs", chrome_prefs)

        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=self.chrome_options)
        

        self.set_location()
        self.driver.set_window_size(500, 500)


    def close_web_driver(self):
        if self.driver:
            self.driver.quit()
            print("Driver quited")
            self.set_profile_free(self.profile['id'])
        if self.profile_in_use:
            self.set_profile_free(self.profile['id'])
        print("Trying to get new order...")
        time.sleep(3)

    def get_all_hrefs(self):
        """
        Gets all hrefs from current web
        """
        elements = self.driver.find_elements(By.TAG_NAME, 'a')
        hrefs = [element.get_attribute("href") for element in elements]
        return hrefs
    
    def get_random_href(self):
        """
        Gets all hrefs and then picks one random href to click it
        """
        hrefs = self.get_all_hrefs()
        random_href = self.pick_random_result(hrefs)
        return random_href


    def random_scroll(self):
        """
        Makes random scroll, used more in mobile version
        """
        random_number = random.randint(-500, 1000)
        self.driver.execute_script(f"window.scrollBy({{top: {random_number}, behavior: 'smooth'}});")


    def make_random_movements_for_given_time(self, work_time=30):
        """
        Makes random movements for given time
        """
        start_time = time.time()
        if time.time() - start_time > work_time:
            print("Reached the specified work time. Stopping.")
        else:
            window_rect = self.driver.get_window_rect()
            width, height = window_rect['width'], window_rect['height']
            start_x = window_rect['x'] + width // 2
            start_y = window_rect['y'] + height // 2
            steps = 0
            # Move the mouse to the center of the browser window
            pyautogui.moveTo(start_x, start_y)
            global random_number
            random_number = 0
            clicked = False
            # Scroll down to the bottom of the page, simulating human-like behavior
            while True:
                if time.time() - start_time > work_time:
                    print("Reached the specified work time. Stopping.")
                    break
                steps += 1


                pyautogui.scroll(random.randint(-500,-50))  # Scroll down
                time.sleep(random.uniform(0.1, 1))  # Random sleep to mimic human behavior

                if random_number == steps:
                    # Get the current mouse position
                    mouse_x, mouse_y = pyautogui.position()

                    # Find clickable elements (like <a> tags with href attributes)
                    clickable_elements = self.driver.find_elements(By.CSS_SELECTOR, "a[href]")

                    for element in clickable_elements:
                        # Get the element's location and size
                        location = element.location
                        size = element.size

                        # Calculate the element's bounding box
                        start_x, start_y = location['x'], location['y']
                        endX, endY = start_x + size['width'], start_y + size['height']

                        # Check if the mouse is within the element's bounding box
                        if start_x <= mouse_x <= endX and start_y <= mouse_y <= endY:
                            print(f"Clicking on element at ({start_x}, {start_y})")
                            pyautogui.click()
                            clicked = True
                            break

                    if not clicked:
                        random_number = steps + random.randint(1, 3)
                    print("Not possible to click on an element at the current mouse position.")
                    # Small mouse movements while scrolling
                move_x = start_x + random.randint(-150, 150)
                move_y = start_y + random.randint(-150, 150)
                pyautogui.moveTo(move_x, move_y, duration=0.2)
                # Check if the end of the page is reached
                if self.driver.execute_script("return window.innerHeight + window.scrollY >= document.body.offsetHeight"):
                    break
            clicked = False
            # Scroll back up to the top of the page
            while True:
                if time.time() - start_time > work_time:
                    print("Reached the specified work time. Stopping.")
                    break
                steps = steps + 1
                # Small mouse movements while scrolling


                pyautogui.scroll(random.randint(50,500))  # Scroll up
                time.sleep(random.uniform(0.1, 1))  # Random sleep to mimic human behavior
                if random_number == steps:
                    # Get the current mouse position
                    mouse_x, mouse_y = pyautogui.position()

                    # Find clickable elements (like <a> tags with href attributes)
                    clickable_elements = self.driver.find_elements(By.CSS_SELECTOR, "a[href]")

                    for element in clickable_elements:
                        # Get the element's location and size
                        location = element.location
                        size = element.size

                        # Calculate the element's bounding box
                        start_x, start_y = location['x'], location['y']
                        endX, endY = start_x + size['width'], start_y + size['height']

                        # Check if the mouse is within the element's bounding box
                        if start_x <= mouse_x <= endX and start_y <= mouse_y <= endY:
                            print(f"Clicking on element at ({start_x}, {start_y})")
                            element.click()
                            clicked = True
                            break

                    if not clicked:
                        random_number = steps + random.randint(1, 3)
                    print("Not possible to click on an element at the current mouse position.")
                move_x = start_x + random.randint(-150, 150)
                move_y = start_y + random.randint(-150, 150)
                pyautogui.moveTo(move_x, move_y, duration=0.2)
                # Check if the top of the page is reached
                if self.driver.execute_script("return window.scrollY == 0"):
                    break

            print("Completed human-like scrolling.")

    def make_random_movements(self):
        """
        Makes random movements of mouse to look like human
        """
        self.make_random_movements_for_given_time(self.order['work_sec'])


    def make_random_movements_with_followup_links(self):
        """
        Makes random movements with follow up links, stays in a link for 30 seconds, than goes to another link for another 30 seconds until work_time reached
        """
        print("\nMaking random movements with follow up links\n")
        start_time = time.time() #Time when we started movements
        work_time = self.order['work_sec']

        self.make_random_movements_for_given_time(random.randint(25, 30))
        href_to_follow_up = self.get_random_href()
        initial_url = self.driver.current_url
        if work_time <=30:
            print("Reached specific time for random movements with follow up links")
        else:
            while True:
                if time.time() - start_time > work_time:
                    print("Reached specific time for random movements with follow up links")
                    break
                try:
                    self.driver.get(href_to_follow_up)
                except:
                    self.driver.get(initial_url)
                print(f"{int(work_time - (time.time() - start_time))} seconds left for more activity")
                self.make_random_movements_for_given_time(random.randint(25, 40))
                try:
                    self.driver.back()
                except:
                    self.driver.get(initial_url)
                self.make_random_movements_for_given_time(random.randint(6, 15))
                href_to_follow_up = self.get_random_href()
                time.sleep(2)

    def test_web_driver(self):
        """
        This webdriver function is for testing, it does not have proxy.
        """
        self.driver = webdriver.Chrome()
        self.driver.get('https://www.google.com')
        self.type_in_input("dyson")
        time.sleep(100)
        self.driver.quit()

    def accept_cookies(self):
        """
        If Cookies button was found, click it 
        """
        try:
            #Click accept cookies button if found
            button = self.driver.find_element(By.ID, 'L2AGLb')
            button.click()
            time.sleep(2)
        except:
            pass

    def start_web_driver(self):
        """
        Sets up web driver
        """   
        self.set_profile() #Gets random profile from django server
        try:
            self.set_chrome_options()
            print("Chrome options set")
            # self.authenticate_proxy()
            self.driver.get("https://www.google.com")
            print("Proxy Authenticated")
            self.accept_cookies()
        except Exception as e:
            print("Error setting up web driver. \t", e)
            self.close_web_driver()

    def type_in_input(self, words):
        try:
            search_input = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.NAME, "q"))
            )
            for character in words:
                search_input.send_keys(character)
                time.sleep(random.uniform(0.1, 0.5))

            search_input.send_keys(Keys.RETURN)
            print("Searched for: ", self.domain)
            time.sleep(2)
        except:
            self.driver.get("https://www.google.com")
            search_input = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.NAME, "q"))
            )
            for character in words:
                search_input.send_keys(character)
                time.sleep(random.uniform(0.1, 0.5))

            search_input.send_keys(Keys.RETURN)
            print("Searched for: ", self.domain)
            time.sleep(2)


    def __check_results(self, xpath):
        """
        :param xpath: XPATH of SPONSORED, Business or SPONSORED Business
        :return: True if found that xpath else False
        """
        try:
            results = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, xpath))
            )
            return results
        except Exception as e:
            return []
        
    def check_results_by_class_name(self, class_name):
        """
        :param xpath: XPATH of SPONSORED, Business or SPONSORED Business
        :return: True if found that xpath else False
        """
        try:
            results = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located(
                    (By.CLASS_NAME, class_name))
            )
            return results
        except Exception as e:
            return []
        
    def collect_item_from_list_of_elements(self, list_of_elements, item):
        """
        Collects the item that we want to collect from the list of elements collected by class_name
        """
        item = item.capitalize()
        for e in list_of_elements:
            found_text = e.text
            print("Found Buttons: ", found_text)
            if item in found_text:
                print(f"Button {item} found successfully")
                return e

        print(f"Could not find {item} Button")
        return None
        
    def __check_results_xpath_template(self, xpath_template):
        """
        Sometimes we have xpaths of same items but with different id's for different websites, this function gets them
        """
        try:
            elements = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, xpath_template))
            )
            return elements
        except Exception as e:
            print(f'Error while fetching with xpath_template: {e}')
            return False
            


    def collect_sponsored_results(self):
        """
        Collects sponsored resutls
        """
        self.sponsored_results = self.__check_results(self.xpaths['Sponsored'])
        return self.sponsored_results

    def collect_business_results(self):
        """
        Collects business location results, 
        Sometimes it shows up as location sometimes as business, if it didnt show as location, we check if it showed up as business.
        """
        self.business_results['results'] = self.collect_location_results()
        if len(self.business_results['results']) < 2:
            print("FOUND LESS THEN 3 Locations")
            self.business_results['results'] = self.__check_results_xpath_template(self.xpaths['Business']['elements_template'])
            self.location_or_business = 'Business'
        return self.business_results['results']

    def collect_location_results(self):
        """
        Collects location results
        """
        results = self.__check_results_xpath_template(self.xpaths['Location']['elements_template'])
        return results if results else []

    def collect_sponsored_business_results(self):
        """
        Collects sponsored businesses
        """
        self.sponsored_business_results['results'] = self.__check_results(self.xpaths['Sponsored business']['elements_template'])
        return self.sponsored_business_results['results']


    def __is_profile_in_use(self, data):
        """
        Checks if profile data is already being used
        param :data: profile data fetched from django server
        """
        return True if data in used_profiles else False
    
    def request_random_profile(self):
        """
        Gets a random profile from django server
        """
        profile_url = "http://" + self.django_url + "/api/get/random/user/web/1"
        response = requests.get(profile_url)
        data = response.json()
        if 'error' in data:
            return None
        self.profile_in_use = True
        return data
    
    def get_profile(self):
        """
        Selects a random profile, checks if its used or None and gets another one
        """        

        profile = self.request_random_profile()
        #while there is no free profile
        while profile is None:
            print("All profiles are busy, checking again")
            time.sleep(2)
            profile = self.request_random_profile()

        if self.__is_profile_in_use(profile):
            print("\nProfile bussy with another order!\n")
            while self.__is_profile_in_use(profile):
                print("Profile is already in use, fetching a new profile...")
                profile = self.request_random_profile()
            print("\nFree profile fetched!\n")
        return profile
    
    def set_profile(self):
        """
        Sets profile data, fetches new profile if fetched profile is not free
        """
        self.profile = self.get_profile()
        used_profiles.append(self.profile)
        self.set_or_create_profile_directory() # creates a profile_dir if it doesnt exist, or just gets the existing profile dir
        print("---------Profile-------------------")
        print(f"Profile id: {self.profile['id']}\nProxy ip: {self.profile['proxy']}")
        print(f"Country: {self.profile['country']}\nRegion: {self.profile['regionName']}\nTimezone: {self.profile['timezone']}")
        print("-----------------------------------")
    
    def fetch_orders_from_web(self):
        """
        Fetches orders in web and saves them in a JSON file
        """
        time.sleep(1)
        url = f"http://{self.django_url}/api/get/orders/web"
        response = requests.get(url)
        if response.status_code == 200:
            orders_data = response.json()[0]
            
            if not orders_data:
                print("There is no order")
      
            self.order = orders_data
            print("\n\n---------Order----------------------")
            print(f"Order: {self.order['domain_name']}")
            print(f"Order ID: {self.order['id']}")
            print(f"Order reached users: {self.order['reached_users']}/{self.order['total_users']}")
            print(f"Order first action: {self.order['action']}")
            print(f"Order second action: {self.order['second_action']}")
            print("------------------------------------\n")
        return []
    
    def __location_improver_popped_up(self):
        """
        Sometimes a popup improve location popps upp, we need to close it, 
        """
        try: 
            WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, '//*[@id="__51MZoC4MKP_ptQPgeqMkAs_8"]/div[2]/span/div'))
            )
            print("Improve Location popped up")

            close_popup_button = button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="__51MZoC4MKP_ptQPgeqMkAs_8"]/div[2]/span/div/div[2]/div[3]/g-raised-button/div/div'))
            )
            close_popup_button.click()
            print("Popup closed")
        except NoSuchElementException:
            pass
        except Exception as e:
            print(f"An error occured: {e}")

    
    def collect_results_by_action(self, action, pick_random_result=False):
        """
        param :action: Decides what type of results to collect (Sponsored, Business or Sponsored Business)
        param :pick_a_random_result: if True sets self.result_to_click to a random result from results list else pass
        return: returns results needed to click
        """

        time.sleep(2)
        if action == "Sponsored":
            results = self.collect_sponsored_results()
        elif action == "Business":
            results = self.collect_business_results()
        elif action == "Sponsored Business":
            results = self.collect_sponsored_business_results()
        else:
            print("Action is not correct!")
            return []
        if pick_random_result:
            self.result_to_click = self.pick_random_result(results)
        if action == "Sponsored":
            self.result_to_click = self.result_to_click.find_element(By.TAG_NAME, 'a')
        self.result_to_click.click()
        print("\n\nClicked result\n")
        return results
    
    def __do_second_action(self):
        """
        Visits website, asks for direction or presses call button based from self.order['second_action']
        """

        if self.location_or_business == "Location":
            action = 'Location'
        else:
            action = 'Business'
        
        if self.order['action'] == "Sponsored":
            time.sleep(5)
            return

        print("ACTION: ", action)
        if self.order['second_action'] == None:
            print("No second action was provided")
            return
        
        buttons_classname = self.xpaths[action]['buttons']
        
        buttons = self.check_results_by_class_name(buttons_classname)
        print(f"Found {len(buttons)} buttons")
        button = self.collect_item_from_list_of_elements(buttons, self.order['second_action'])
        if button:
            button.click()
        else:
            print("Button to click has not been found. Finishing order and closing window")            
        print("SECOND ACTION FINISHED!")
    

    def pick_random_result(self, results):
        """
        param :results: list of results
        return: returns 1 result from results list if list is not empty, else returns None
        """
        if not results:
            print("No results available.")
            return None
        return random.choice(results)
    
    def move_mouse_to_position(self, new_position):
        """
        Moves mouse from current position to new position
        param :new_position: new_position = int x, int y
        """        
        new_x, new_y = new_position
        
        duration = random.uniform(0.5, 1)

        pyautogui.moveTo(new_x, new_y, duration=duration)
        
        print("Made a mouse movement")



    def random_mouse_movements(self, time_duration=10, total_num_of_moves=None):
        """
        total_duration: Total duration of time how much time should we be making a random mouse movement
        total_num_of_moves: if this param is given, time duration gets ignored, and we can move mouse how many times is this given.
        """
        current_x, current_y = pyautogui.position()
        start_time = time.time()
        print("DOING RANDOM MOUSE MOVEMENTS")

        current_num_of_moves = 0

        #Condition based on time or num_of_moves   
        while (total_num_of_moves is not None and current_num_of_moves < total_num_of_moves) or \
              (total_num_of_moves is None and time.time() - start_time < time_duration):
            
            move_x = random.randint(-50, 50)
            move_y = random.randint(-100, 100)
            
            # # Calculate the new position
            new_x = current_x + move_x
            new_y = current_y + move_y

            new_position = new_x, new_y

            self.move_mouse_to_position(new_position)

            current_num_of_moves += 1 if total_num_of_moves else 0
            time.sleep(random.uniform(0.5, 3))


        print("RANDOM MOVEMENTS FINISHED")

    def get_element_position(self, element):
        location = element.location
        size = element.size
        center_x = location['x'] + size['width'] / 2
        center_y = location['y'] + size['height'] / 2
        return center_x, center_y

    def update_reached_users(self, pk):
        """
        Updates the reached users
        """
        url = "http://" + self.django_url + f'/api/update-reached-numbers/{pk}/'
        response = requests.post(url)
        print("Updated reached users: ", response.json())

    def set_profile_free(self, pk):
        """
        Updates if profile is being used
        """
        if self.profile['id']:
            self.profile_in_use = False
            if self.profile in used_profiles:
                used_profiles.remove(self.profile)
            url = "http://" + self.django_url + f'/api/set/profile/free/{pk}/'
            try:
                response = requests.post(url)
                print("Updated profile inUsed: ", response.json())
            except Exception as e:
                print("\nServer is down. \nError: ", e)

    
    def is_click_domain_only(self):
        """
        Returns True if we have to go directly to the given domain no matter if it finds that domain in first page or no
        """
        return self.order['click_domain_only']


    def search_google(self):
        self.start_web_driver()
        print("\n\n Started web driver\n")
        self.parsed_url = urlparse(self.order['domain_name'])
        self.domain = self.parsed_url.netloc or self.parsed_url.path
        self.type_in_input(self.domain) #Types in input the word, in this case the domain
        self.solve_captcha() #Solves captcha if it was found

        if self.is_click_domain_only():
            """
            If we have to follow to a given domain no matter if we find that result or no, we scroll, go to that domain and scroll again.
            """
            self.make_random_movements_for_given_time(random.randint(15, 30))
            time.sleep(2)
            self.driver.get(self.order['domain_name'])
            self.make_random_movements_with_followup_links()
        else:
            # self.__location_improver_popped_up()
            self.collect_results_by_action(self.order['action'], pick_random_result=True)
            self.__do_second_action()
            self.make_random_movements_with_followup_links()
            time.sleep(5)
            print("Finished order!")

    def full_action(self):
        while True:
            try:
                self.fetch_orders_from_web()
                self.search_google()
                self.close_web_driver()
                print("\nProfile is being unused now!!")
                self.update_reached_users(self.order['id'])
                print("\nUpdated reached users now!!")
            except Exception as e:
                if len(self.order)>0:
                    print(f"Error happened, action interrupted. {e}")
                self.close_web_driver()

    
class MobileBot(Bot):

    def __init__(self):
        super().__init__()

        self.proxy = None
        self.xpaths = {
            'Sponsored' : "//span[text()='Sponsored']//ancestor::div[contains(@class, 'xpd')]",
            'Location': {
                'parent': '//*[@id="Odp5De"]/div/div/div[1]/div[2]',
                'elements_template': '//*[contains(@class, "nitkue")]',
                'first_element': '//*[@id="Odp5De"]/div/div/div[1]/div[2]/div[1]/div/div[2]/div[1]/div/div[1]',#//*[@id="tsuid_144"] 
                'second_element': '//*[@id="Odp5De"]/div/div/div[1]/div[2]/div[1]/div/div[2]/div[1]/div/div[2]',#//*[@id="tsuid_145"]
                'third_element': '//*[@id="Odp5De"]/div/div/div[1]/div[2]/div[1]/div/div[2]/div[1]/div/div[3]',#//*[@id="tsuid_146"]
                'buttons': 'GytWRb',
            },
            'Business': {
                'parent': '//*[@id="rso"]/div[7]/div/div/div[1]/div[4]',
                'elements_template': '//*[contains(@class, "rllt__details")]',
                'elements': "//div[@class='uMdZh tIxNaf rllt__borderless']//a[@role='link']", 
                'buttons': 'PSVhtb', #bkaPDb
            },
            'Sponsored business': {
                'parent': "//div[@id='taw']",
                'elements_template': "(//div[@class='yDDB0e'])",#Q6JQs
                'buttons': '',
            }
        }

    def fetch_orders_from_web(self):
        """
        Fetches orders in web and saves them in a JSON file
        """
        time.sleep(1)
        url = f"http://{self.django_url}/api/get/orders/mobile"
        response = requests.get(url)

        if response.status_code == 200:
            orders_data = response.json()[0]

            if not orders_data:
                print("There is no order")
      
            self.order = orders_data
            print("\n\n---------Order----------------------")
            print(f"Order: {self.order['domain_name']}")
            print(f"Order ID: {self.order['id']}")
            print(f"Order reached users: {self.order['reached_users']}/{self.order['total_users']}")
            print(f"Order first action: {self.order['action']}")
            print(f"Order second action: {self.order['second_action']}")
            print("------------------------------------\n")
        return []

    def test_web_driver(self):
        """
        Test web driver
        """
        user_agent = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/125.0.6422.145 Mobile/15E148 Safari/604.1"
        options = Options()
        options.add_argument(f'--user-agent={user_agent}')
        self.driver = webdriver.Chrome(options=options)
        self.driver.get('https://www.amazon.com/')
        self.order['work_sec'] = 300   
        self.make_random_movements()
        time.sleep(200)
        self.driver.quit()



    def open_tabs(self, num_of_tabs=3):
        for i, tab in enumerate(range(num_of_tabs)):
            self.driver.execute_script("window.open('https://www.google.com');")
            new_window_handle = self.driver.window_handles[-1]
            self.driver.switch_to.window(new_window_handle)
            self.type_in_input(f"Searching for tab {i}")

    def collect_item_from_list_of_elements(self, list_of_elements, item):
        """
        Collects the item that we want to collect from the list of elements collected by class_name
        """
        items = {
            "website": "WEBSITE",
            "direction": "DIRECTIONS",
            "call": "CALL"    
        }
        print(f"Looking for: {items[item]} button\n")
        print("Found: ", [e.text for e in list_of_elements], "Buttons")
        for e in list_of_elements:
            found_text = e.text
            if items[item] in found_text:
                print(f"{items[item]} Button Found successfully")
                return e
        print("Checking for second template")

        list_of_elements = self.check_results_by_class_name("bkaPDb")
        
        print("Found: ", [e.text for e in list_of_elements], "Buttons")
        for e in list_of_elements:
            found_text = e.text
            if items[item].lower().capitalize() in found_text:
                print(f"{items[item]} Button Found successfully")
                return e
        print(f"Could not find {items[item]} Button")
        return None

    def request_random_profile(self):
        """
        Requests a random profile from django server
        """
        profile_url = "http://" + self.django_url + "/api/get/random/user/mobile/1"
        response = requests.get(profile_url)
        data = response.json()
        if 'error' in data:
            return None
        self.profile_in_use = True
        return data
    
    def make_random_movements_for_given_time(self, work_time=30):
        """
        Makes random movements such as scrolls in mobile version for a given work time.
        """
        print(f"\nMaking Random Movements for {work_time} seconds\n")
        start_time = time.time()
        
        wait_time = random.randint(2, 4)

        if time.time() - start_time > work_time:
            print("Reached the specified work time. Stopping.")
        else:
            while True:
                if time.time() - start_time > work_time:
                    break
                self.random_scroll()
                time.sleep(wait_time)


def multiple_mobile_threads(num_of_threads=6):
    """
    Creates a bot for each thread to work independently from each other 
    """
    threads = []
    bots = []
    #starting bots
    for i, bot in enumerate(range(num_of_threads)):
        bot_instance = MobileBot()
        bots.append(bot_instance)
    #Starting threads
    for i, bot in enumerate(bots):
        time.sleep(3)
        thread = threading.Thread(target=bot.full_action)
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()



# If u are using mobile version uncomment multiple_mobile_threads() function

multiple_mobile_threads(num_of_threads=7)



#If you are using web version uncomment those two lines of code.

# bot = Bot()
# bot.full_action()
