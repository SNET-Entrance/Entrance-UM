import base64
from flask import request, make_response
from flask_login import current_user
from flask_user import login_required

from fexplorer import fexplorer
import os
import json
from const import basedir


@fexplorer.route('/list', methods=['POST'])
@login_required
def list_files():
    data = json.JSONDecoder().decode(request.data)
    if 'path' not in data or data['path'] == '':
        data['path'] = os.path.join(basedir, 'data', str(current_user.id))
    if not os.path.exists(data['path']):
        return make_response('', 404)
    if not data['path'].startswith(os.path.join(basedir, 'data', str(current_user.id))):
        return make_response('', 403)

    if 'type' not in data or data['type'] == '':
        valids = ''
    else:
        valids = tuple(data['type'])

    results = list()
    for file in os.listdir(data['path']):
        if file.endswith(valids):
            results.append(file)

    return make_response(json.dumps(results))


@fexplorer.route('/get', methods=['POST'])
@login_required
def get_file():
    data = json.JSONDecoder().decode(request.data)
    if 'path' not in data or data['path'] == '':
        return make_response('', 400)
    if not os.path.isfile(data['path']):
        return make_response('', 404)
    if not data['path'].startswith(os.path.join(basedir, 'data', str(current_user.id))):
        return make_response('', 403)

    f = open(data['path'], 'rb').read()
    out = { 'path': data['path'], 'payload': base64.b64encode(f) }
    return make_response(json.dumps(out), 200)


@fexplorer.route('/fexplorer', methods=['POST'])
@login_required
def list_dirs():
    path = os.path.join(basedir, 'data', str(current_user.id)) + request.form['dir']
    if not os.path.exists(path):
        return make_response('', 404)

    try:
        location = os.listdir(path)
        dirs = list()
        files = list()
        output = '<ul class="jqueryFileTree">'
        for entry in location:
            if os.path.isdir(path + entry):
                dirs.append('<li class="directory collapsed"><a rel="' + path + entry + '/">' + entry + '</a></li>')
            if os.path.isfile(path + entry) and request.form['onlyFolders'] == 'false':
                files.append('<li class="file ext_' + os.path.splitext(entry)[1].replace('.', '') + '"><a rel="' + path + entry + '">' + entry + '</a></li>')

        output += ''.join(dirs + files)
        output += '</ul>'
    except:
        output = '<ul class="jqueryFileTree"></ul>'

    return make_response(output, 200)


@fexplorer.route('/fexplorer/upload', methods=['POST'])
@login_required
def upload_file():
    file = request.files['file']
    file.save(os.path.join(basedir, 'data', str(current_user.id), file.filename))
    return make_response('', 200)