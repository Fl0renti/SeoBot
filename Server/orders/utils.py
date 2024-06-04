import requests
from bs4 import BeautifulSoup
from lxml import etree
from .models import Keyword, Order, Profile
import random
from SEOBot.settings import PROXY
import re

def is_valid_domain(domain):
    # Regular expression pattern for domain name validation
    domain_pattern = r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$"
    
    # Check if the domain matches the pattern
    if re.match(domain_pattern, domain):
        return True
    else:
        return False


def get_results(results, business_type, attr_type, find_or_find_all='find_all', domain_type='web'):
    html_dict = {
        "normal" : {
            "html": {
                "attr": "div",
                "class": "MjjYud"
            },
            "text": {
                "attr": "h3",
                "class": "LC20lb"
            }
        },

        "sponsored": {
            "html": {
                "attr": "div",
                "class": "uEierd"#vdQmEd
            },
            "text": {
                "attr": "a",
                "class": "sVXRqc"
            }
        },

        "business": {
            "html": {
                "attr": "div",
                "class": "dbg0pd" if domain_type == 'web' else 'JIFdL'#web M8OgIe dbg0pd, mobile  lrl-obh
            }
        },
        "sponsored_business": {
            "html": {
                "attr": "div",
                "class": "ixr6Zb"
            }
        }
    }
    if find_or_find_all == 'find':
        return results.find(html_dict[business_type][attr_type]['attr'], class_=html_dict[business_type][attr_type]['class'])
    else:
        return results.find_all(html_dict[business_type][attr_type]['attr'], class_=html_dict[business_type][attr_type]['class'])

def get_a_random_proxy(domain_type):
    profile_ids = Profile.objects.filter(domain_type=domain_type).values_list('id', flat=True)

    if profile_ids:
        # Select a random primary key
        random_id = random.choice(profile_ids)
        
        # Retrieve the random profile by its primary key
        random_profile = Profile.objects.get(id=random_id)
        
        proxy_not_final = random_profile.proxy.split(":")
        proxy = "http://" + proxy_not_final[2] + ':' + proxy_not_final[3] + '@' + proxy_not_final[0] + ':' + proxy_not_final[1]

        return proxy
    

def __save_response_to_html(html_content, file_path='output.html'):
    """
    Saves html content in a HTML File
    """
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(html_content)


def search_google_for_keyword(instance, num_results=50, proxy=PROXY):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
    } if instance.domain_type == 'web' else {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/125.0.6422.80 Mobile/15E148 Safari/604.1'
    }
    
    proxy = get_a_random_proxy(instance.domain_type)

    url = f"https://www.google.com/search?q={instance.domain_name}&num={num_results}"
    response = requests.get(url, headers=headers, proxies={'http': proxy, 'https': proxy})

    # __save_response_to_html(response.text)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # normal_results = get_results(results, 'normal', 'html')
        sponsored_results = [r.find('a').text.strip() for r in get_results(soup, 'sponsored', 'html', domain_type=instance.domain_type)]
        business_results = [r.text.strip() for r in get_results(soup, 'business', 'html', domain_type=instance.domain_type)]
        sponsored_businesses = [r.text.strip() for r in get_results(soup, 'sponsored_business', 'html', domain_type=instance.domain_type)]
        
        has_sponsored = False
        has_business = False 
        has_sponsored_business = False 

        has_sponsored = len(sponsored_results) > 0
        has_business = len(business_results) > 0
        has_sponsored_business = len(sponsored_businesses) > 0

        profile = Profile.objects.order_by('?').first()
        if has_sponsored:
            print("HAS SPONSORED: ", has_sponsored)
        elif has_business:
            print("HAS PLACE: ", has_business)
        elif has_sponsored_business:
            print("HAS SPONSORED PLACE: ", has_sponsored_business)
        else:
            print("ONLY NORMAL RESULTS FOUND")
        print("PROFILE: ", profile.domain_type)
        Keyword.objects.create(
            keyword = instance,
            has_sponsored = has_sponsored,
            has_business = has_business,
            has_sponsored_business = has_sponsored_business,
            profile = profile,
            status = "Waiting"
        )

        return True

    return False



