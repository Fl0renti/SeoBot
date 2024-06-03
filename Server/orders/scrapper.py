import requests

def scraping_process_complete(order_pk):
    url = f'http://127.0.0.1:8000/update-reached-users/{order_pk}/'
    response = requests.get(url)
    if response.json().get('success'):
        print('Reached users count updated successfully.')
    else:
        print('Error updating reached users count.')

# Send ID of order
scraping_process_complete(2) 



