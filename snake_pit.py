import csv
import json
import time
from collections import defaultdict

from typing import (
  Dict,
  List,
)

import requests
from fuzzywuzzy import process as fuzzy

import firebase_admin
from firebase_admin import (
  credentials,
  firestore,
)

cred = credentials.Certificate('sa.json')
firebase_admin.initialize_app(credentials.Certificate('sa.json'))
fdb = firestore.client()




open_businesses = fdb.collection('business').where('is_closed', '==', False).stream()

name_to_id = defaultdict(list)
for doc in open_businesses:
  business_name = doc.to_dict().get('business_name', '')
  if business_name:
    name_to_id[business_name].append(doc.id)

print(f'Found {len(name_to_id)} unique names.')

res = fuzzy.extract('firewings', name_to_id.keys())
res = dict(res)

print(res)







exit(0)


##########################
# Don't look below here. #
##########################





yelp_business_search_endpoint = 'https://api.yelp.com/v3/businesses/search'
yelp_headers = {
  'Authorization': 'Bearer ',
}

def get_businesses_around_zip(zipcode) -> list:
  """Return a list of businesses from the Yelp API around a zipcode"""
  params = {
    'term': 'restaurant',
    'location': str(zipcode),
    'price': '1,2',
    'radius': '3219',  # 3219m,  ~2mi
  }
  resp = requests.get(
    yelp_business_search_endpoint,
    params=params,
    headers=yelp_headers
  )
  if resp.status_code != 200:
    print(f'ERROR: Status code {resp.status_code}')
    return []
  else:
    print(f'Processing zipcode {zipcode}')
    resp_dict = resp.json()
    print(f'Got {resp_dict.get("total")} businesses')
    return resp_dict.get('businesses', [])


def get_all_businesses():
  """Write all businesses around zipcodes in zipcodes.txt to businesses.json"""
  results: Dict[str, list] = {}

  with open('zipcodes.txt', 'r') as f:
    for zipcode in f.readlines():
      zipcode = zipcode.rstrip()
      time.sleep(0.1)
      results[zipcode] = get_businesses_around_zip(zipcode)

  with open('businesses.json', 'w') as f:
    json_str = json.dumps(results)
    f.write(json_str)

    # data_json_str = json.dumps(data['businesses'][0])
    # # print(data_json_str)

    # unique_categories=[]
    # for business in data['businesses']:
    #   categories = business.get('categories')

    #   # for i in range(len(categories)):
    #     # cat_title = categories[i]['title']
    #   for category in categories:
    #     cat_title = category['title']

    #     if cat_title not in unique_categories:
    #     #  print(cat_title)
    #     unique_categories.append(cat_title)


def generate_zipcodes_csv():
  """Call Zipcode API and write results to zipcode_api_data.csv"""
  api_key = 'xFI1c3UiR92LjWPtDviJBeuvPX1VQKtsfaG8xYdDMB69o185JKc12U9bsctt1nfd'
  ENDPOINT = 'https://www.zipcodeapi.com/rest/{api_key}/radius.csv/94605/10/mile'

  resp = requests.get(ENDPOINT.format(api_key=api_key))

  if resp.status_code != 200:
    raise Exception(f"Status code wasn't 200. It was {resp.status_code}.")

  zipcodes = resp.content #.decode()
  with open('zipcode_api_data.csv', 'wb') as f:
    f.write(zipcodes)


def write_unique_zipcodes_from_zipcodes_csv():
  """Isolate zipcodes from zipcodes_api_data.csv"""

  unique_zip=[]

  with open('zipcode_api_data.csv', 'r') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
    unique_zip = [row.get('zip_code') for row in reader]

    # for row in reader:
    #   #print(row)
    #   zip_code = row['zip_code']
    #   if zip_code not in unique_zip:
    #     unique_zip.append(zip_code)
    #     print(zip_code)

  with open('zipcodes.txt', 'w') as f:
    f.write("\n".join(unique_zip))

    # # gen = (statement<<item>> for <item> in <collection>)
    # <statement> = (<val_if_true> if <condition> else <val_if_false>)
    # [<statement> for <item> in <iterable> if <condition>]

    # result="\n".join((zipcode for zipcode in unique_zip))
    # f.write(result)

    # for zipcode in unique_zip:
    #   f.write(zipcode + "\n")

    #print(json.dumps(zipcodes, indent=2))

    # for zipcode in zipcodes:
    #   zip_code = zipcode['zip_code']
    #   print(zip_code)


zip_to_business = {}
all_businesses = []
unique_businesses = {}

def verify_alias_ID(all_businesses):
  """
  Works for a List of Dicts. Finds any Aliases that have multiple IDs
  """
  from collections import defaultdict
  # defaultdict will create a default value, if someone tries to access it with a key it doesn't have. It will generate the default value for the argument passed to it.
  # in this case, we pass it the list type. so on key access, if the key doesn't exist, it will create [] in its place
  alias_id = defaultdict(list)
  # for example, if I try to append 'myId' to alias_id['myAlias']
  alias_id['myAlias'].append('myId')
  # this doesn't throw an error. instead,
  print(alias_id['myAlias'])  # ['myId']



  alias_id = {}

  for business in all_businesses:
    bus_id = business['id']
    bus_alias = business['alias']

    # this if statement could be removed with alias_id = defaultdict(list) because `bus_id not in alias_id[bus_alias]` will make alias_id[bus_alias] have a default of [].
  #   if bus_alias not in alias_id:
  #       alias_id[bus_alias] = []
  #   if bus_id not in alias_id[bus_alias]:
  #     alias_id[bus_alias].append(bus_id)
  # #print(alias_id)

  print('Checking for Alias with multiple IDs')
  no_multiple_ids = 'True'
  for key in alias_id:
    if len(alias_id[key])>=2:
      print(key, alias_id[key], '\n')
      no_multiple_ids = 'False'
  if no_multiple_ids == 'True':
      print('Aliases have their own unique IDs')
  print('Done')



with open('businesses.json', 'r') as f:
  zip_to_business = json.loads(f.read())

for zipcode, businesses in zip_to_business.items():
  for business in businesses:
    all_businesses.append(business)
    # Assumes aliases are unique
    unique_businesses[business['alias']] = business


# Make results more predictable
unique_businesses = dict(sorted(unique_businesses.items()))

# verify_alias_ID(all_businesses)

"""
####Tests for verify_alias_ID function
sample_business = unique_businesses[list(unique_businesses.keys())[0]]

sample_businessA = sample_business.copy()
sample_businessA['id']='AAAAAAAAAAAA'

# 2 dict of bus w/ same Alias and same IDs.Should return 'Aliases have their own IDs'
sample_business1 = [sample_business,sample_business]

# 2 dict of bus w/ same Alias but different IDs. Should return business, [IDs].
sample_business2 = [sample_business,sample_businessA]

verify_alias_ID(sample_business1)
verify_alias_ID(sample_business2)
####End Test
"""

"""
## What businesses have we found, and how many?

# # Print all business aliases
# for business_alias in sorted(unique_businesses.keys()):
#   print(business_alias)

num_unique_businesses = len(unique_businesses)
print(f'Found {len(all_businesses)} businesses.')
print(f'Found {num_unique_businesses} unique businesses.')


## How many of them have phone numbers listed? How many are open?

open_businesses = []
businesses_with_phone = []
for business_alias, business in unique_businesses.items():
  if not business.get('is_closed'):
    open_businesses.append(business_alias)
  if business.get('phone'):
    businesses_with_phone.append(business_alias)

print(f'Found {len(businesses_with_phone)} businesses with phone numbers.')
print(f'Found {len(open_businesses)} open businesses.')

### Which businesses don't have phone numbers?
businesses_wo_phone = set(open_businesses) - set(businesses_with_phone)
b_wo_p_str = '\n  '.join(businesses_wo_phone)
print(f'{len(businesses_wo_phone)} open businesses without phone: ')
print(f'  {b_wo_p_str}')
"""


target_yelp_business = unique_businesses[list(unique_businesses.keys())[0]]
# print('--------------')
# print(json.dumps(target_yelp_business, indent=2))
# print('--------------')

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



import firebase_admin
from firebase_admin import (
  credentials,
  firestore,
)

cred = credentials.Certificate('sa.json')
firebase_admin.initialize_app(cred)
fdb = firestore.client()

# businesses_ref = db.collection(u'business')
# docs = businesses_ref.stream()

# for doc in docs:
#   # print(u'{} => {}'.format(doc.id, doc.to_dict()))
#   print(json.dumps(doc.to_dict(), indent=2))







bus_to_write = {
  "business_name" : target_yelp_business['name'],
  "alias": target_yelp_business['alias'],
  "is_closed" : target_yelp_business['is_closed'],
  "is_enabled" : False,
  "phone": target_yelp_business['phone'],
  "location": {
    "address1": target_yelp_business['location']['address1'],
    "address2": target_yelp_business['location']['address2'],
    "address3": target_yelp_business['location']['address3'],
    "city": target_yelp_business['location']['city'],
    "coordinates": {
      "latitude": target_yelp_business['coordinates']['latitude'],
      "longitude": target_yelp_business['coordinates']['longitude'],
    },
  },
  "hours": {
    "source": "yelp",
    "type": "json",
    "body": "",
  },
}

def write_yelp_bus_to_firestore(firestore_db, yelp_business) -> bool:
  """
  Add a new Yelp business to the database uwu
  yelp_business is a dictionary of an indiv. business
  """

  bus_to_write = {
    "business_name" : yelp_business['name'],
    "alias": yelp_business['alias'],
    "is_closed" : yelp_business['is_closed'],
    "is_enabled" : False,
    "phone": yelp_business['phone'],
    "location": {
      "address1": yelp_business['location']['address1'],
      "address2": yelp_business['location']['address2'],
      "address3": yelp_business['location']['address3'],
      "city": yelp_business['location']['city'],
      "coordinates": {
        "latitude": yelp_business['coordinates']['latitude'],
        "longitude": yelp_business['coordinates']['longitude'],
     },
    },
    "hours": {
      "source": "yelp",
      "type": "json",
      "body": "",
   },
  }

  try:
    bus_ref = firestore_db.collection('business').document("y_" + yelp_business['id'])
    # TODO: make new bus_to_write based on yelp_business

    print('-------------------- ' +'\n' + json.dumps(bus_to_write, indent=1))
    # bus_ref.set(bus_to_write)

  except Exception as e:
    print(e)
    return False

  else:
    return True

"""
      Adds businesses from unique_businesses into Firebase
for aliases in unique_businesses.keys():
  # aliases are keys in unique_businesses
  # TODO: call write_yelp_bus_to_firestore with every yelp business
  write_yelp_bus_to_firestore(fdb, unique_businesses[aliases])
"""

'''
  bus_ref = fdb.collection('business').document("y_" + target_yelp_business['id'])
  bus_ref.set(bus_to_write)
'''

{
  "business_name": "{bname}",
  "is_closed": False,
  "is_enabled": True,
  "location": {
    "address1": "124 Second St",
    "address2": "",
    "address3": "",
    "city": "San Francisco",
    "coordinates": {
      "latitude": "37.787789124691",
      "longitude": "-122.399305736113",
    },
  },
  "hours": {
    "source": "yelp",
    "type": "json",
    "body": "{\"open\":[{\"is_overnight\":false,\"start\":\"1000\",\"end\":\"2300\",\"day\":0},{\"is_overnight\":false,\"start\":\"1000\",\"end\":\"2300\",\"day\":1},{\"is_overnight\":false,\"start\":\"1000\",\"end\":\"2300\",\"day\":2},{\"is_overnight\":false,\"start\":\"1000\",\"end\":\"2300\",\"day\":3},{\"is_overnight\":false,\"start\":\"1000\",\"end\":\"2330\",\"day\":4},{\"is_overnight\":false,\"start\":\"1000\",\"end\":\"2330\",\"day\":5},{\"is_overnight\":false,\"start\":\"1000\",\"end\":\"2300\",\"day\":6}],\"hours_type\":\"REGULAR\"}",
  }
}

def business_id(bid):
  # TODO: Define and document possible parameters
  print(f'Received BID: {bid}')

  bid_ref = fdb.collection('business').document(bid)
  bid_doc=bid_ref.get()

  if bid_doc.exists:
    print(u'Document data: {}'.format(bid_doc.to_dict()))
  else:
    print ('No such document')

bid0 = 'y_FI0veywHLcErYNMxFePqng'
bid1 = 'bbbbbb'

# business_id(bid0)
# business_id(bid1)
