import json
import time
import requests
from configs.config import *

def fetch_orders_and_save_web():
    # Replace this URL with the actual URL where your Django view is hosted
    time.sleep(1)
    url = f"http://{DjangoURL}/api/get/orders/web"

    # Make the GET request to the view
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Load the JSON data from the response
        orders_data = response.json()


        # Specify the file name where you want to save the data
        file_name = ORDERS_LIST_Web_JSON
        if not orders_data:
            print("There is no orders")
        # Write the JSON data to a file
        with open(file_name, 'w') as json_file:
            json.dump(orders_data, json_file, indent=4)

    else:
        print("Failed to fetch orders data")





