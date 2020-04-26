import json
from collections import defaultdict

import firebase_admin
from fuzzywuzzy import process
from flask import (
  Flask,
  jsonify,
  request,
  Response,
)
from firebase_admin import (
  credentials,
  firestore,
)

cred = credentials.Certificate('sa.json')
firebase_admin.initialize_app(cred)
fdb = firestore.client()

app = Flask('app')


@app.route('/businesses')
def businesses():
  """Return a list of business IDs in JSON"""
  bids = [doc.id for doc in fdb.collection('business').stream() if doc.to_dict()['is_enabled'] is True]
  return jsonify(bids)

@app.route('/businesses/search')
def business_search():
  """Return a list of business IDs from a business_search"""
  location = request.args.get('location', '')
  q = request.args.get('q', '').lower()
  strict = False if request.args.get('strict', 'false').lower() == 'false' else True
  # print(f'/businesses/search: q="{q}" location={location} strict={strict}')

  open_businesses = fdb.collection('business').where('is_closed', '==', False).stream()
  name_to_id = defaultdict(list)
  alias_to_id = defaultdict(list)
  matched_ids_from_zip = []
  for doc in open_businesses:
    business_name = doc.to_dict().get('business_name', '').lower()
    if business_name:
      name_to_id[business_name].append(doc.id)

    alias = doc.to_dict().get('alias', '').lower()
    if alias:
      alias = alias.replace('-', ' ')
      if alias[-1].isdigit():
        alias = alias[:-1]
      alias_to_id[alias].append(doc.id)


    zipcode = doc.to_dict().get('location', {}).get('zip_code', '')
    if location and zipcode:
      matched_ids_from_zip.append(doc.id)

  print(f'Found {len(name_to_id)} unique names.')

  bids = []
  if location != '':
    bids = matched_ids_from_zip
  elif strict:
    bids = name_to_id.get(q) or []
  else:  # fuzzy search
    fuzzy_res = process.extract(q, alias_to_id.keys())
    names = dict(fuzzy_res).keys()
    for alias in dict(fuzzy_res).keys():
      bids.extend(alias_to_id[alias])
  return jsonify(bids)


@app.route('/business/<bid>')
def business_id(bid):
  # Fetches document and possible parameters
  print(f'Received BID: {bid}')
  is_alias = True if request.args.get('type', '') == 'alias' else False
  if is_alias:
    bid_ref = fdb.collection('business'
    ).where('alias', '==', bid
    ).limit(1)
    try:
      bid_doc=next(bid_ref.stream())
    except:
      bid_doc=None
  else:
    bid_ref = fdb.collection('business').document(bid)
    bid_doc=bid_ref.get()

  result = None
  if getattr(bid_doc, 'exists', False):
    result = jsonify(bid_doc.to_dict())
  else:
    result = Response("{}", status=204, mimetype='application/json')

  return result


@app.route('/')
def main():
  return "."


app.run(host='0.0.0.0', port=8080)
