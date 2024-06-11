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


import os
import zipfile

from selenium import webdriver
import time

PROXY_HOST = '209.38.175.1'  # rotating proxy or host
PROXY_PORT = 31112 # port
PROXY_USER = 'rw46xu2d' # username
PROXY_PASS = 'pof78YiH1qoyIFOh' # password


manifest_json = """
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

background_js = """
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


def get_chromedriver(use_proxy=False, user_agent=None):
    path = os.path.dirname(os.path.abspath(__file__))
    chrome_options = webdriver.ChromeOptions()
    if use_proxy:
        pluginfile = 'proxy_auth_plugin.zip'

        with zipfile.ZipFile(pluginfile, 'w') as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", background_js)
        chrome_options.add_extension(pluginfile)
    if user_agent:
        chrome_options.add_argument('--user-agent=%s' % user_agent)
    driver = webdriver.Chrome(chrome_options)
    return driver
