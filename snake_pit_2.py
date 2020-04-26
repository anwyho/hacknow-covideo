import csv
import json
import os
import requests
import time

from collections import defaultdict
from typing import Callable, Dict

import fuzzywuzzy
from fuzzywuzzy import process

import firebase_admin
from firebase_admin import (
  credentials,
  firestore,
)

cred = credentials.Certificate('sa.json')
firebase_admin.initialize_app(cred)
fdb = firestore.client()

yelp_business_search_endpoint = 'https://api.yelp.com/v3/businesses/'
yelp_headers = {
  'Authorization': f'Bearer {os.getenv("YELP_API_KEY")}',
}




def edit_business(bid: str, edit_func: Callable[[dict], dict]) -> None:
  """
  :param bid: Business ID
  :param edit_func: The function to modify business.
  """
  bid_doc = fdb.collection('business').document(bid)
  bid_doc_snap = bid_doc.get()

  if bid_doc_snap.exists:
    business = bid_doc_snap.to_dict()

    business = edit_func(business)

    bid_doc.set(business)
  else:
    print( 'bid ' + bid + ' not found.')

### Edit Funcs

def mark_business_as_closed(business: dict) -> dict:
  business['is_closed'] = True
  return business


def enable_business(business: dict) -> dict:
  business['is_enabled'] = True
  return business


### Edit Func Factory

def set_business_hours_edit_func_factory(hours_dict: dict) -> Callable[[dict], dict]:

  def set_business_hours(business: dict) -> dict:
    business['hours'] = hours_dict
    return business

  return set_business_hours


def set_location_edit_func_factory(location_dict: dict) -> Callable[[dict],dict]:

  def set_location(business: dict) -> dict:
    business['location'] = location_dict
    return business

  return set_location




def get_yelp_business_ids():
  business_ids = []
  docs = fdb.collection('business').stream()
  for doc in docs:

    #print(dir(doc))

    bid = doc.id
    if bid.startswith('y_'):
      bid = bid[2:]
      business_ids.append(bid)
  return business_ids


def backfill_yelp_business_hours():
  yelp_bids = get_yelp_business_ids()
  num_bids = len(yelp_bids)
  start_from = 0
  for i, yelp_bid in enumerate(yelp_bids[start_from:], start=start_from+1):
    print(f'{i}/{num_bids} bids processed. Processing: y_{yelp_bid}')
    endpoint = yelp_business_search_endpoint + str(yelp_bid)
    resp = requests.get(endpoint, headers=yelp_headers)
    if resp.status_code != 200:
      print(f'Error: {yelp_bid}')
      continue
    body = resp.json()
    hours_str = json.dumps(body.get('hours', []))

    hours_dict = {
      'body': hours_str,
      'source': 'yelp',
      'type': 'json',
    }
    edit_func: Callable[[dict], dict] = set_business_hours_edit_func_factory(hours_dict)
    edit_business(f'y_{yelp_bid}', edit_func)


def backfill_yelp_locations():
  yelp_bids = get_yelp_business_ids()
  num_bids = len(yelp_bids)
  start_from = 0
  for i, yelp_bid in enumerate(yelp_bids[start_from:], start=start_from+1):
    print(f'{i}/{num_bids} bids processed. Processing: y_{yelp_bid}')
    endpoint = yelp_business_search_endpoint + str(yelp_bid)
    resp = requests.get(endpoint, headers=yelp_headers)
    if resp.status_code != 200:
      print(f'Error: {yelp_bid}')
      continue
    body = resp.json()
    # location_str = json.dumps(body.get('location', []))

    empty_location = {
      "address1": "",
      "address2": "",
      "address3": "",
      "city": "",
      "zip_code": "",
      "country": "",
      "state": "",
      "display_address": [],
    }

    location_dict = body.get('location', empty_location)

    # Clean up location dict
    location_dict['address1'] = location_dict.get('address1', '')
    location_dict['address2'] = location_dict.get('address2', '')
    location_dict['address3'] = location_dict.get('address3', '')
    if 'cross_streets' in location_dict:
      del location_dict['cross_streets']

    edit_func: Callable[[dict], dict] = set_location_edit_func_factory(location_dict)
    edit_business(f'y_{yelp_bid}', edit_func)


# print(yelp_headers)
# backfill_yelp_business_hours()
backfill_yelp_locations()


# # Closure example

# specific_list = []
# def closure_ex():
#   print(specific_list)

# closure_ex()  # []

# specific_list.append('uh-oh')
# closure_ex()  # prints ['uh-oh']




# def make_num_incr_printer(start: int) -> Callable[[int], None]:
#   def num_printer(increment: int) -> None:
#     return start + increment
#   return num_printer








def business_enable(bid):
  # turns the "is_enabled" parameter for a business from False to True

  bid_doc = fdb.collection('business').document(bid)
  bid_doc_snap = bid_doc.get()

  if bid_doc_snap.exists:
    business = bid_doc_snap.to_dict()
    business['is_enabled'] = True
    bid_doc.set(business)
  else:
    print( 'bid ' + bid + ' not found.')


def enable_all_businesses():
  bid_docs = fdb.collection('business').stream()
  for bid_doc in bid_docs:
    business_enable(bid_doc.id)


sample_business_str = """
{
  "id": "HYbKSGCg8hqLw6J_X7qbyQ",
  "alias": "acqua-e-farina-hayward",
  "name": "Acqua e Farina",
  "image_url": "https://s3-media1.fl.yelpcdn.com/bphoto/Xr
-8-jNL-J4IfblqkjFIYQ/o.jpg",
  "is_closed": false,
  "url": "https://www.yelp.com/biz/acqua-e-farina-hayward?
adjust_creative=zarYjf84bP7MP5CJiBGX9A&utm_campaign=yelp_a
pi_v3&utm_medium=api_v3_business_search&utm_source=zarYjf8
4bP7MP5CJiBGX9A",
  "review_count": 927,
  "categories": [
    {
      "alias": "italian",
      "title": "Italian"
    },
    {
      "alias": "desserts",
      "title": "Desserts"
    },
    {
      "alias": "cocktailbars",
      "title": "Cocktail Bars"
    }
  ],
  "rating": 4.5,
  "coordinates": {
    "latitude": 37.6725627,
    "longitude": -122.0824255
  },
  "transactions": [
    "delivery"
  ],
  "price": "$$",
  "location": {
    "address1": "22622 Main St",
    "address2": "",
    "address3": "",
    "city": "Hayward",
    "zip_code": "94541",
    "country": "US",
    "state": "CA",
    "display_address": [
      "22622 Main St",
      "Hayward, CA 94541"
    ]
  },
  "phone": "+15108881568",
  "display_phone": "(510) 888-1568",
  "distance": 272.3692783972094
}
"""

bid0 = 'y_FI0veywHLcErYNMxFePqng'
bid1 = 'bbbbbb'

# business_id(bid0)
# business_id(bid1)


def modify_doc(bid):

  bid_doc = fdb.collection('business').document(bid)
  bid_doc_snap = bid_doc.get()


