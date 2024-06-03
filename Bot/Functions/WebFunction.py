import random
import re
import time
from collections import Counter
from urllib.parse import urlparse, urljoin

import pyautogui
import requests
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
RandomNumber = random.randint(3,7)

def get_paths_from_url(url):
    paths = set()
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        for link in soup.find_all('a', href=True):
            link_url = urljoin(url, link['href'])
            parsed_link = urlparse(link_url)
            if parsed_link.netloc == urlparse(url).netloc and parsed_link.path:
                paths.add(parsed_link.path)
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    return paths
def visitRandomUrl(driver, url):
    try:
        paths = get_paths_from_url(url)
        pathsList = list(paths)
        words = [re.split('/|-|_', path.strip('/')) for path in pathsList]
        flat_words = [word for sublist in words for word in sublist if word != '']
        word_counts = Counter(flat_words)
        most_common_word = word_counts.most_common(1)
        print(f"The most common word in window is: {most_common_word[0][0]} with {most_common_word[0][1]} occurrences.")
        news_paths = [path for path in pathsList if f'/{most_common_word[0][0]}' in path]
        random_word = random.choice(news_paths)
        url_to_visit = f"{url.rstrip('/')}{random_word}"
        driver.get(url_to_visit)
    except:
        driver.get(url)



def center_mouse_and_scroll(driver,url,start_time,WorkTime):
    if time.time() - start_time > WorkTime:
        print("Reached the specified work time. Stopping.")
    else:
        window_rect = driver.get_window_rect()
        width, height = window_rect['width'], window_rect['height']
        start_x = window_rect['x'] + width // 2
        start_y = window_rect['y'] + height // 2
        steps = 0
        # Move the mouse to the center of the browser window
        pyautogui.moveTo(start_x, start_y)
        global RandomNumber
        clicked = False
        # Scroll down to the bottom of the page, simulating human-like behavior
        while True:
            if time.time() - start_time > WorkTime:
                print("Reached the specified work time. Stopping.")
                break
            print("--------")

            print(RandomNumber)
            print(steps)
            print("--------")
            steps = steps +1


            pyautogui.scroll(random.randint(-500,-50))  # Scroll down
            time.sleep(random.uniform(0.1, 1))  # Random sleep to mimic human behavior

            if RandomNumber == steps:
                # Get the current mouse position
                mouseX, mouseY = pyautogui.position()

                # Find clickable elements (like <a> tags with href attributes)
                clickable_elements = driver.find_elements(By.CSS_SELECTOR, "a[href]")

                for element in clickable_elements:
                    # Get the element's location and size
                    location = element.location
                    size = element.size

                    # Calculate the element's bounding box
                    startX, startY = location['x'], location['y']
                    endX, endY = startX + size['width'], startY + size['height']

                    # Check if the mouse is within the element's bounding box
                    if startX <= mouseX <= endX and startY <= mouseY <= endY:
                        print(f"Clicking on element at ({startX}, {startY})")
                        pyautogui.click()
                        clicked = True
                        break

                if not clicked:
                    RandomNumber = steps + random.randint(1, 3)
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
            if time.time() - start_time > WorkTime:
                print("Reached the specified work time. Stopping.")
                break
            steps = steps + 1
            # Small mouse movements while scrolling


            pyautogui.scroll(random.randint(50,500))  # Scroll up
            time.sleep(random.uniform(0.1, 1))  # Random sleep to mimic human behavior
            if RandomNumber == steps:
                # Get the current mouse position
                mouseX, mouseY = pyautogui.position()

                # Find clickable elements (like <a> tags with href attributes)
                clickable_elements = driver.find_elements(By.CSS_SELECTOR, "a[href]")

                for element in clickable_elements:
                    # Get the element's location and size
                    location = element.location
                    size = element.size

                    # Calculate the element's bounding box
                    startX, startY = location['x'], location['y']
                    endX, endY = startX + size['width'], startY + size['height']

                    # Check if the mouse is within the element's bounding box
                    if startX <= mouseX <= endX and startY <= mouseY <= endY:
                        print(f"Clicking on element at ({startX}, {startY})")
                        element.click()
                        clicked = True
                        break

                if not clicked:
                    RandomNumber = steps + random.randint(1, 3)
                print("Not possible to click on an element at the current mouse position.")
            move_x = start_x + random.randint(-150, 150)
            move_y = start_y + random.randint(-150, 150)
            pyautogui.moveTo(move_x, move_y, duration=0.2)
            # Check if the top of the page is reached
            if driver.execute_script("return window.scrollY == 0"):
                break
        visitRandomUrl(driver,url)

        print("Completed human-like scrolling.")