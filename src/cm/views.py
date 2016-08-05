import json
import os

import struct

import requests
from flask import request, make_response
from flask_user import login_required, current_user

from bootstrap import db, cont_ext, policy_mode, kex_url
from bootstrap.models import AttrAuth
from cm import cm, models
from const import basedir


@cm.route('', methods=['GET'])
@login_required
def show_containers():
    containers = models.Container.query.filter_by(user_id=current_user.id)  # load container of a user

    out = list()
    for c in containers:
        entry = c.dict()
        entry['files'] = [f.dict() for f in c.files]
        out.append(entry)

    out.reverse()  # reverse to have most recent on tob
    return make_response(json.dumps(out), 200)  # response JSON serialized


@cm.route('', methods=['POST'])
@login_required
def add_container():
    data = json.JSONDecoder().decode(request.data)
    if 'name' not in data or 'files' not in data:
        return make_response('', 400)  # error missing parameter

    if not data['files']:
        return make_response('', 400)  # error missing parameter

    if 'output_path' in data:
        output_path = os.path.join(data['output_path'], data['name'] + cont_ext)  # if output_path is specified use it
    else:
        output_path = os.path.join(basedir, 'data', str(current_user.id), data['name'] + cont_ext)  # otherwise generate it

    container = models.Container(data['name'], output_path, policy_mode, current_user.id)  # create container
    db.session.add(container)  # and store it persistently
    db.session.commit()

    for f in data['files']:  # iterate through submitted files array
        if 'path' not in f or 'type' not in f or 'policy' not in f:
            return make_response('', 400)  # error missing file parameter

        if not os.path.isfile(f['path']):
            return make_response('', 404)  # error file does not exist

        # TODO: delete created container in error case

        f['policy'] = f['policy'].replace(', ', ',').replace(': ', ':')  # parse submitted policy
        policy = models.Policy.generate(f['policy'], current_user)  # create file
        db.session.add(models.File(f['path'], f['type'], policy, f['policy'], container.id))  # store in DB
    db.session.commit()

    # serialize container for response
    out = container.dict()
    out['files'] = list()
    for f in container.files:
        out['files'].append(f.dict())

    # generate AA parameter
    aa_param = dict()
    aa_param['files'] = list()
    for f in out['files']:
        aa_param['files'].append({
            "path": f['path'],
            "type": f['type'],
            "policy": f['policy']
        })
    aa_param['outfile'] = container.path
    aa_param['owner'] = {'emails': [current_user.email]} # embed identity of user into container

    aa_response = AttrAuth.encrypt_container(container, aa_param) # start encryption
    if aa_response is None:
        return make_response('', 500) # error AA error

    return make_response(json.dumps(out), 201) # successful encryption


@cm.route('/<container_id>', methods=['POST'])
@login_required
def reencrypt(container_id):
    container = models.Container.query.filter_by(id=container_id).first_or_404()
    if container not in current_user.container:
        return make_response('', 403) # error unauthorized access

    if container.reencrypt(current_user) is None:
        return make_response('', 500) # error during encryption

    return make_response('', 200) # success


@cm.route('/policy', methods=['POST'])
@login_required
def evaluate():
    # to evaluate a policy while it is typed
    policy = request.data.replace(', ', ',').replace(': ', ':') # parse policy
    users = models.Policy.evaluate(policy, current_user) # compute authorized set of contacts
    out = list()
    for user in users:
        tmp = user.dict()
        tmp['properties'] = [p.dict() for p in user.properties]
        tmp['attributes'] = [a.dict() for a in user.attributes if not a.sys]
        out.append(tmp)

    return make_response(json.dumps(out), 200) # return set JSON serialized


@cm.route('/<container_id>', methods=['GET'])
@login_required
def show_container(container_id):
    # show status of container
    # can be used to check status of ongoing encryption processes
    container = models.Container.query.filter_by(id=container_id).first_or_404()
    if container not in current_user.container:
        return make_response('', 403)

    out = container.dict()
    out['files'] = list()
    for f in container.files:
        out['files'].append(f.dict())

    aa_response = AttrAuth.status_container(container)
    if aa_response['success'] is False:
        return make_response(aa_response['msg'], 500)
    else:
        out['status'] = aa_response['status']

    return make_response(json.dumps(out), 200)


@cm.route('/<container_id>', methods=['PUT'])
@login_required
def edit_container(container_id):
    # this method can be used to modify the name of the path of a container
    container = models.Container.query.filter_by(id=container_id).first_or_404()
    if container not in current_user.container:
        return make_response('', 403)

    data = json.JSONDecoder().decode(request.data)
    if 'name' not in data or 'path' not in data:
        return make_response('', 400)

    container.name = data['name']
    container.path = data['path']
    db.session.add(container)
    db.session.commit()
    return make_response(json.dumps(container.dict()), 200)


@cm.route('/<container_id>', methods=['DELETE'])
@login_required
def delete_container(container_id):
    # to delete a container
    container = models.Container.query.filter_by(id=container_id).first_or_404()
    if container not in current_user.container:
        return make_response('', 403)

    db.session.delete(container)
    db.session.commit()

    if os.path.exists(container.path) and os.path.isfile(container.path):
        os.remove(container.path)

    # TODO: inform AA about deletion - otherwise errors occur

    # TODO: container.type = 1, uuids[] dissociate from users

    return make_response('', 200)


@cm.route('/decrypt', methods=['POST'])
@login_required
def decrypt_container():
    # to decrypt a cipher text
    data = json.JSONDecoder().decode(request.data)
    print data
    if 'container' not in data or 'outputDirectory' not in data:
        return make_response('', 400) # error missing parameters

    # extract manifest of a container
    # to receive identity of sender
    x = open(data['container'], 'rb')
    x.read(11)
    len = struct.unpack('>Q', x.read(8))[0]
    x.read(32)
    manifest = x.read(len)
    x = json.JSONDecoder().decode(manifest)

    # fetch secret key of sender identity generated for user
    kex_request = requests.get(
            kex_url + '/keys/' + x['owner']['emails'][0] + '?access_token=' + current_user.kex_access_token)
    if kex_request.status_code != 200:
        return make_response('', 500) # KEX error

    # send repective secret key to AA
    data['user'] = {'privateKey': kex_request.text}

    aa_response = AttrAuth.decrypt_container(json.dumps(data))
    if aa_response['success'] is False:
        return make_response(aa_response['msg'], 500) # error during the decryption

    return make_response('', 200)


@cm.route('/<container_id>/download', methods=['GET'])
@login_required
def download_container(container_id):
    # to download a container
    container = models.Container.query.filter_by(id=container_id).first_or_404()
    if container not in current_user.container:
        return make_response('', 403)

    f = open(container.path, 'rb').read()
    response = make_response(f)

    # set header field to indicate a file download for browser
    response.headers['Content-Disposition'] = 'attachment; filename=' + container.name + cont_ext
    return response
