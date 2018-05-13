import requests
import json
import os

user = str()
oauth_key = str()
oauth_sec = str()

if os.path.isfile('backup.conf'):
    with open('backup.conf') as conf:
        conf = [c.strip() for c in conf.readlines()]

    for c in conf:
        c = c.replace(' ', '')
        if c.startswith('user='):
            user = c[5:]
        if c.startswith('oauth_key='):
            oauth_key = c[11:]
        if c.startswith('oauth_sec='):
            oauth_sec = c[11:]

if not user:
    print('ERROR: user not defined')
if not oauth_key:
    print('ERROR: oauth key not defined')
if not oauth_sec:
    print('ERROR: oauth secret key not defined')
if not user or not oauth_key or not oauth_sec:
    return 1
