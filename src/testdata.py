import json
import random

import requests

baseurl = 'http://localhost:5000'
access_token = '?access_token=' + '6fDnYGsmSO1eIJR9uExo8e34RXPFeE'

testdata = open('mock.csv', 'r')
attrs = open('attrs.txt', 'r').read().split(',')

for row in testdata:
    name, email = row.replace('\n', '').split(',')
    param = json.dumps({ 'name': name, 'email': email })

    n = random.randint(8, 12)
    i = random.randint(0, len(attrs)-n)
    uattrs = attrs[i:i+n]

    response = requests.post(baseurl + '/contacts' + access_token, data=param)
    if response.status_code == 201:
        id = json.JSONDecoder().decode(response.text)['id']
        for a in uattrs:
            response = requests.post(baseurl + '/contacts/' + str(id) + '/attributes' + access_token, data=json.dumps({ 'name': a }))
        print 'Successfully added ' + name + '<' + email + '>'