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
from Bot.configs.config import captcha_profile_dir

import time
import pyautogui
import random
import sys
import os
from urllib.parse import urlparse
import requests
import shutil


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
        self.__profile_dir = None
        self.profile_in_use = False

        self.mobile_emulation = {
            "deviceMetrics": {"width": 360, "height": 640, "pixelRatio": 3.0}
        }

        self.parsed_url = ""
        self.domain = ""
        self.profile = {}
        self.order = {}

        self.__sponsored_results_xpath = "//span[text()='Sponsored']//ancestor::div[contains(@class, 'xpd')]"
        self.__business_results_xpath = ""
        self.__sponsored_business_results_xpath = ""

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
            

    def __authenticate_proxy(self):

        """
        passes the authentication of proxy when starting webbrowser
        :return:
        """
        self.driver.get("https://www.google.com")
        time.sleep(2)
        pyautogui.typewrite(self.profile['proxyusername'])
        pyautogui.press('tab')
        pyautogui.typewrite(self.profile['proxypassword'])
        pyautogui.press('enter')
        self.driver.get("https://www.google.com")

    def __create_new_profile_dir_from_existing_profile(self):
        """
        Copies main profile directory with 2captcha installed on it into a new profile directory
        """
        main_profile_dir = captcha_profile_dir
        if not os.path.exists(self.__profile_dir):
            shutil.copytree(main_profile_dir, self.__profile_dir)
            print(f'{self.__profile_dir} created')
        


    def __set_or_create_profile_directory(self):
        """
        Creates profile directory if this profile directory does not exist, else does not create directory
        if it catches OS Error, logs the reason why didnt it do its job.
        """
        self.__profile_dir = os.path.join(os.getcwd(), f'Resources/Profiles/profile{self.profile["id"]}')
        try:
            self.__create_new_profile_dir_from_existing_profile()
        except OSError as e:
            print(f"Could not create directory {self.__profile_dir}: {e}")
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
        self.chrome_options.add_argument(f"user-data-dir={self.__profile_dir}")
        self.chrome_options.add_argument(f"--proxy-server={self.profile['proxy']}")
        self.chrome_options.add_argument("--verbose")
        self.chrome_options.add_argument(f"user-agent={self.profile['UserAgent']}")

        chrome_prefs = {
            "profile.default_content_setting_values.geolocation": 1,  # Allow geolocation
            "timezone": self.profile["timezone"]
        }
        self.chrome_options.add_experimental_option("prefs", chrome_prefs)

        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=self.chrome_options)

        self.set_location()
        # self.driver.maximize_window()


    def close_web_driver(self):
        if self.driver:
            self.driver.quit()
            print("Driver quited")
            self.set_profile_free(self.profile['id'])
        if self.profile_in_use:
            self.set_profile_free(self.profile['id'])
        print("Proceeding to next order...")
        time.sleep(3)



    def make_random_movements(self, driver, start_time, work_time):
        """
        Makes random movements of mouse to look like human
        """
        if time.time() - start_time > work_time:
            print("Reached the specified work time. Stopping.")
        else:
            window_rect = driver.get_window_rect()
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
                    clickable_elements = driver.find_elements(By.CSS_SELECTOR, "a[href]")

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
                if driver.execute_script("return window.innerHeight + window.scrollY >= document.body.offsetHeight"):
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
                    clickable_elements = driver.find_elements(By.CSS_SELECTOR, "a[href]")

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
                if driver.execute_script("return window.scrollY == 0"):
                    break

            print("Completed human-like scrolling.")


    def test_web_driver(self):
        """
        This webdriver function is for testing, it does not have proxy.
        """
        self.driver = webdriver.Chrome()
        self.driver.get('https://www.google.com')
        self.type_in_input("dyson")
        time.sleep(100)
        self.driver.quit()

    def start_web_driver(self):
        """
        Sets up web driver
        """   
        self.set_profile() #Gets random profile from django server
        try:
            self.set_chrome_options()
            print("Chrome options set")
            self.__authenticate_proxy()
            print("Proxy Authenticated")
        except Exception as e:
            print("Error setting up web driver. \t", e)
            self.close_web_driver()

    def type_in_input(self, words):

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
    
    def set_profile(self):
        """
        Sets profile data, fetches new profile if fetched profile is not free
        """
        profile = self.get_random_profile()
        
        #while there is no free profile
        while profile is None:
            print("All profiles are busy, checking again")
            time.sleep(3)
            profile = self.get_random_profile()

        if self.__is_profile_in_use(profile):
            print("\nProfile bussy with another order!\n")
            while self.__is_profile_in_use(profile):
                print("Profile is already in use, fetching a new profile...")
                profile = self.get_random_profile()
            print("\nFree profile fetched!\n")
        self.profile = profile
        used_profiles.append(self.profile)
        self.__set_or_create_profile_directory() # creates a profile_dir if it doesnt exist, or just gets the existing profile dir
        print("---------Profile-------------------")
        print(f"Profile id: {self.profile['id']}\nProxy ip: {self.profile['proxy']}")
        print(f"Country: {self.profile['country']}\nRegion: {self.profile['regionName']}\nTimezone: {self.profile['timezone']}")
        print("-----------------------------------")
        
    def get_random_profile(self):
        """
        Gets a random profile from django server
        """
        profile_url = "http://" + self.django_url + "/api/get/random/user/web/2"
        response = requests.get(profile_url)
        data = response.json()
        if 'error' in data:
            return None
        self.profile_in_use = True
        return data
    
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
            response = requests.post(url)
            print("Updated profile inUsed: ", response.json())

    
    def search_google(self):
        self.start_web_driver()
        print("\n\n Started web driver\n")
        self.parsed_url = urlparse(self.order['domain_name'])
        self.domain = self.parsed_url.netloc or self.parsed_url.path

        self.type_in_input(self.domain) #Types in input the word, in this case the domain
        self.solve_captcha() #Solves captcha if it was found
        # self.__location_improver_popped_up()
        self.collect_results_by_action(self.order['action'], pick_random_result=True)
        self.__do_second_action()
        start_time = time.time()
        work_time = self.order['work_sec']
        self.make_random_movements(self.driver, start_time, work_time)
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
        driver = webdriver.Chrome(options=options)
        driver.get('https://www.dyson.com/en')
        start_time = time.time()
        self.fetch_orders_from_web()
        work_time = self.order['work_sec']
        print("WORK TIME: ", work_time)
        self.make_random_movements(driver, start_time, work_time)
        time.sleep(100)
        driver.quit()

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

    def get_random_profile(self):
        """
        Gets a random profile from django server
        """
        profile_url = "http://" + self.django_url + "/api/get/random/user/mobile/2"
        response = requests.get(profile_url)
        data = response.json()
        if 'error' in data:
            return None
        self.profile_in_use = True
        return data
    



bot = Bot()
bot.full_action()
# print(bot.order)

# print(bot.result_to_click)
####Arange to take non scheduled first, take 1 result
####If there is no None Scheduled, then proceed with scheduled if its time came


#Worktime sa me nejt ne website merret prej orderit, jo ne google search
#Ne search mun me bo 1 pun randome
#Ne baz te aksionit kena me zgjedh me kliku njanen prej sponsorave, 
#Nese jan ma shum se 1 me u kliku 1 sponsor random ose lokacion random
#Nese veq 1 kliko qato sponsor