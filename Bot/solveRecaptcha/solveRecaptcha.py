import sys
import os
from twocaptcha import TwoCaptcha
def solveRecaptcha(sitekey,url):
    # https://github.com/2captcha/2captcha-python

    sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

    

    api_key = os.getenv('APIKEY_2CAPTCHA', '655d459592883cff8558721556138828')

    solver = TwoCaptcha(api_key)
    try:
        result = solver.solve_captcha(
            site_key=sitekey,
            page_url=url)

    except Exception as e:
        print(e)

    else:
        return result
