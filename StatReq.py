#  StatReq - doesn't work because of access restrictions on RotoWire

import requests

#This URL will be the URL that your login form points to with the "action" tag.
#PostLoginURL = 'https://www.rotowire.com/users/login.php'
PostLoginURL = 'https://www.rotowire.com/users/login.php?go=%2Fmlbcommish19%2Findex2.htm'

#This URL is the page you actually want to pull down with requests.
RequestURL = 'https://www.rotowire.com/mlbcommish19/nl_pit.asp?mth=10&dy=12&yr=2019'

PAYLOAD = {
    'username': 'kmbart',
    'password': 'rotowire56'
}

with requests.Session() as session:
    post = session.post(PostLoginURL, data=PAYLOAD)
    res  = session.get(RequestURL)

if res.status_code == requests.codes.ok:
    print(res.status_code)
    print(res.headers['content-type'])

    if len(res.text) < 25000:
        print(res.text)
    else:
        print('Text more than 25,000 characters')
else:
    print('Invalid response from requests')

