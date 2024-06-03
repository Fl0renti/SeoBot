import requests
from configs.config import DjangoURL

def scraping_process_complete(order_pk):
    url = f'http://{DjangoURL}/update-reached-users/{order_pk}/'
    response = requests.get(url)
    if response.json().get('success'):
        print('Reached users count updated successfully.')
    else:
        print('Error updating reached users count.')


def scraping_process_incomplete(order_pk):
    url = f'http://{DjangoURL}/update-reached-users-incomplete/{order_pk}/'
    response = requests.get(url)
    if response.json().get('success'):
        print('count updated successfully.')
    else:
        print('Error updating reached users count.')



def setProfileFree(pk):
    url = f'http://{DjangoURL}/api/set/profile/free/{pk}/'
    response = requests.get(url)
    if response.json().get('success'):
        print('Profile is set free.')
    else:
        print('Error updating reached users count.')
