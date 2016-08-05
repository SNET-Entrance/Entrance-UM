import base64
import json

import requests
from flask import redirect, url_for, request, make_response
from flask.ext.login import current_user
from flask.ext.user import login_required

from bootstrap import app, umcm_client_id, umcm_client_secret, kex_url, db


@app.route('/', methods=['GET'])
def welcome():
    return redirect(url_for('at.index'))

@app.route('/kex_auth', methods=['POST'])
@login_required
def kex_auth():
    data = json.JSONDecoder().decode(request.data)
    if 'username' not in data or 'password' not in data:
        return make_response('', 400)

    # set authorization header with client_id and client_secret of the umcm
    # client is registered during install of the kex
    headers = {
        'Authorization': 'Basic ' + base64.b64encode(umcm_client_id + ':' + umcm_client_secret)
    }
    params = {
        'grant_type': 'password',
        'username': data['username'],
        'password': data['password']
    }
    key_request = requests.get(kex_url + '/oauth/token', params=params, headers=headers)
    if key_request.status_code != 200:
        return make_response('', 400)

    # store the access token persistently
    kex_response = json.JSONDecoder().decode(key_request.text)
    current_user.kex_access_token = kex_response['access_token']
    db.session.add(current_user)
    db.session.commit()

    return make_response('', 200)