import random
import time
import logging
import re
from db import get_mongo_client
from fastapi import HTTPException
import requests


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def make_request(url, headers):
    session = requests.Session()
    try:
        response = session.post(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Request failed: {e}")
        return None


def scrape_and_append_to_mongodb():
    try:
        # MongoDB connection within a context manager
        with get_mongo_client() as client:
            db = client['mymarket']
            collection = db['phones']

            delay = random.uniform(1, 20)
            time.sleep(delay)
            headers = {
                "User-Agent": ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                               'AppleWebKit/537.36 (KHTML, like Gecko) '
                               'Chrome/91.0.4472.124 Safari/537.36')
            }

            url = 'https://api2.mymarket.ge/api/ka/products?' \
                  'CatID=600&Limit=28&Page=1&SortID=1'
            content = make_request(url, headers)

            if content and 'data' in content and 'Prs' in content['data']:
                products_data = content['data']['Prs']

                for product in products_data:
                    product_info = {
                        'user_id': product.get('user_id'),
                        'user': product.get('user'),
                        'username': product.get('username'),
                        'order_date': product.get('order_date'),
                        'loc_id': product.get('loc_id'),
                        'price': product.get('price'),
                        'currency_id': product.get('currency_id'),
                        'quantity': product.get('quantity'),
                        'weight': product.get('weight'),
                        'views': product.get('views'),
                        'rating': product.get('rating'),
                        'product_id': product.get('product_id'),
                        'title': product.get('title'),
                        'description': product.get('descr'),
                    }
                    collection.insert_one(product_info)
                    logger.info(f"Product with ID {product_info['product_id']}\
                                 inserted into the database.")

    except Exception as e:
        logger.exception(f"An error occurred: {e}")


def extract_number_from_url(url: str) -> str:
    # Use regular expression to extract the desired number
    match = re.search(r'/pr/(\d+)', url)

    if match:
        return match.group(1)
    else:
        raise HTTPException(status_code=400, detail="Invalid URL format")
