import json
from flask import render_template, request, make_response
from flask_user import login_required, current_user
from at import at
from bootstrap import models, db

@at.route('/', methods=['GET'])
@login_required
def index():
    return render_template('index.html', url_prefix=at.url_prefix)

@at.route('/tresor/', methods=['GET'])
@login_required
def index_tresor():
    return render_template('index.html', url_prefix=at.url_prefix)

@at.route('/pages/', methods=['GET'])
@login_required
def get_pages():
    return make_response(current_user.pages, 200)

@at.route('/pages/', methods=['POST'])
@login_required
def store_pages():
    data = json.JSONDecoder().decode(request.data)
    print json.dumps(data)

    current_user.pages = json.dumps(data)
    db.session.add(current_user)
    db.session.commit()
    return make_response('', 200)