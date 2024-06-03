from selenium.webdriver.common.by import By
from twocaptcha import TwoCaptcha
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver



def solve_recaptcha(url, sitekey):
    print("Solving Captcha")
    solver = TwoCaptcha("655d459592883cff8558721556138828")
    response = solver.recaptcha(sitekey=sitekey, url=url)
    code = response['code']
    print(f"Successfully solved the Captcha. The solve code is {code}")
    return code