from flask import Flask, render_template, request
from random import choice
import requests
import urllib.parse


web_site = Flask(__name__)


@web_site.route('/')
def index():
	return render_template('index.html')

@web_site.route('/businessSubmit')
def index2():
	return render_template('businessSubmit.html')



@web_site.route('/business/', defaults={'business_id': None})
@web_site.route('/business/<business_id>/')
def generate_business(business_id):
  if not business_id:
    business_id = request.args.get('business_id')
    
  if not business_id:
    return 'Sorry error something, malformed request.'

  
  wesp = requests.get('https://hacknow-backend--anwyho.repl.co/business/'+ 'fire-wings-hayward' + '?type=alias')
  wesp_dict = wesp.json()

  import json
  wesp_dict['hours'] = json.loads(wesp_dict['hours']['body'])

  print(wesp_dict)

  
  return render_template('business.html', tesp_dict=wesp_dict)

@web_site.route('/search')
def business_search(): 
  """Return a list of businesses from a business_search"""
  location = request.args.get('location', '')
  q = request.args.get('q', '')
  q = urllib.parse.quote(q)

  resp = requests.get('https://hacknow-backend--anwyho.repl.co/businesses/search?q='+ q +'&strict=false')
  resp_list = resp.json()
  bis_id = resp_list[0]
  print(bis_id)

  wesp = requests.get('https://hacknow-backend--anwyho.repl.co/business/'+ bis_id)
  wesp_dict = wesp.json()
  print(wesp_dict)

  bis_id = resp_list[1]
  print(bis_id)
  mesp = requests.get('https://hacknow-backend--anwyho.repl.co/business/'+ bis_id)
  mesp_dict = mesp.json()


  bis_id = resp_list[2]
  print(bis_id)
  kesp = requests.get('https://hacknow-backend--anwyho.repl.co/business/'+ bis_id)
  kesp_dict = kesp.json()

  bis_id = resp_list[3]
  print(bis_id)
  aesp = requests.get('https://hacknow-backend--anwyho.repl.co/business/'+ bis_id)
  aesp_dict = aesp.json()

  bis_id = resp_list[4]
  print(bis_id)
  Leonardo = requests.get('https://hacknow-backend--anwyho.repl.co/business/'+ bis_id)
  Leonardo_dict = Leonardo.json()

  template_params = {
    "wesp_dict": wesp_dict,
    "mesp_dict": mesp_dict,
    "kesp_dict": kesp_dict,
    "aesp_dict": aesp_dict,
    "Leonardo_dict": Leonardo_dict,
  }

  # return redirect(url_for('business', bis_id))
  return render_template('search.html', **template_params)

web_site.run(host='0.0.0.0', port=8080)