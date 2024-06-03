import json
import os
import logging
def get_root_folder():
    return os.getcwd()

NUMBER_OF_THREADS=10
ORDERS_LIST_JSON = f"{get_root_folder()}/Resources/Orders.json"
ORDERS_LIST_Web_JSON = f"{get_root_folder()}/Resources/OrdersWeb.json"
ORDERS_LIST_Mobile_JSON = f"{get_root_folder()}/Resources/OrdersMobile.json"
USERS_AGENTS_Mobile_JSON = f"{get_root_folder()}/Resources/userAgents/mobile.json"
USERS_AGENTS_Tablet_JSON = f"{get_root_folder()}/Resources/userAgents/tablet.json"
USERS_AGENTS_Web_JSON = f"{get_root_folder()}/Resources/userAgents/web.json"
NUMBER_OF_THREADS = 10
LOGS = f"{get_root_folder()}/Resources/Logs/"
DjangoURL = "127.0.0.1:8000"
