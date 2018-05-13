import requests
import json
import os, sys

# Variable declaration
user = str()
oauth_key = str()
oauth_sec = str()

# If file exsts read all lines, strip and remove spaces
if os.path.isfile('backup.conf'):
    with open('backup.conf') as conf:
        conf = [c.strip().replace(' ', '') for c in conf.readlines()]

    # Check each read line and split them around the = sign if they starts with one of the settings
    for c in conf:
        if c.startswith('user='):
            user = c.split('=')[1]
        if c.startswith('oauth_key='):
            oauth_key = c.split('=')[1]
        if c.startswith('oauth_sec='):
            oauth_sec = c.split('=')[1]

# Print which variables remained empty and exit if any is
if not user:
    print('ERROR: user not defined')
if not oauth_key:
    print('ERROR: oauth key not defined')
if not oauth_sec:
    print('ERROR: oauth secret key not defined')
if not user or not oauth_key or not oauth_sec:
    sys.exit(1)
else:
    print('user =', user)
    print('oauth_key =', oauth_key)
    print('oauth_sec =', oauth_sec)

# Get likes using api url and print response and message
likes = f"http://api.tumblr.com/v2/blog/{user}.tumblr.com/likes?api_key={oauth_key}"
likes = requests.get(likes)
likes = json.loads(likes.text)

print(likes['meta']['status'], likes['meta']['msg'])
