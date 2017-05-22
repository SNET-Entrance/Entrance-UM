import requests
import time

from bootstrap import db, aa_url, kex_url
from flask_user import UserMixin
import json

# helper function for performance tests
millis = lambda: int(round(time.time() * 1000))

# helper class used for JSON serialization
class Ext(object):
    def __repr__(self):
        return unicode(self.__dict__)

    def dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

# the user class
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False, server_default='')
    reset_password_token = db.Column(db.String(100), nullable=False, server_default='')


    email = db.Column(db.String(255), nullable=False, unique=True)
    confirmed_at = db.Column(db.DateTime())

    active = db.Column('is_active', db.Boolean(), nullable=False, server_default='0')
    first_name = db.Column(db.String(100), nullable=False, server_default='')
    last_name = db.Column(db.String(100), nullable=False, server_default='')

    # children of a user
    contacts = db.relationship('Contact', backref='user', cascade='all, delete-orphan', lazy='joined')
    attributes = db.relationship('Attribute', backref='user', cascade='all, delete-orphan', lazy='joined')
    container = db.relationship('Container', backref='user', cascade='all, delete-orphan', lazy='joined')
    fitfiles = db.relationship('FitFile', backref='user', cascade='all, delete-orphan', lazy='joined')
    page_default = {'name': 'My Dashboard', 'slug': 'my-dashboard', 'widgets': list()}
    pages = db.Column(db.Text, nullable=True, server_default=json.dumps([page_default]))

    # access token to authenticate against kex exchange service
    kex_access_token = db.Column(db.Text, nullable=False, server_default='')

# flask-oauthlib required classes
class Client(db.Model, Ext):
    name = db.Column(db.String(40))
    description = db.Column(db.String(400))
    user_id = db.Column(db.ForeignKey('user.id'))
    user = db.relationship('User')
    client_id = db.Column(db.String(40), primary_key=True)
    client_secret = db.Column(db.String(55), unique=True, index=True, nullable=False)
    is_confidential = db.Column(db.Boolean)
    _redirect_uris = db.Column(db.Text)
    _default_scopes = db.Column(db.Text)

    @property
    def client_type(self):
        if self.is_confidential:
            return 'confidential'
        return 'public'

    @property
    def redirect_uris(self):
        if self._redirect_uris:
            return self._redirect_uris.split()
        return []

    @property
    def default_redirect_uri(self):
        return self.redirect_uris[0]

    @property
    def default_scopes(self):
        if self._default_scopes:
            return self._default_scopes.split()
        return []


class Grant(db.Model, Ext):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    user = db.relationship('User')
    client_id = db.Column(db.String(40), db.ForeignKey('client.client_id'), nullable=False)
    client = db.relationship('Client')
    code = db.Column(db.String(255), index=True, nullable=False)
    redirect_uri = db.Column(db.String(255))
    expires = db.Column(db.DateTime)
    _scopes = db.Column(db.Text)

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self

    @property
    def scopes(self):
        if self._scopes:
            return self._scopes.split()
        return []


class Token(db.Model, Ext):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.String(40), db.ForeignKey('client.client_id'), nullable=False)
    client = db.relationship('Client')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User')
    token_type = db.Column(db.String(40))
    access_token = db.Column(db.String(255), unique=True)
    refresh_token = db.Column(db.String(255), unique=True)
    expires = db.Column(db.DateTime)
    _scopes = db.Column(db.Text)

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self

    @property
    def scopes(self):
        if self._scopes:
            return self._scopes.split()
        return []

# static class to handle communication with AA
class AttrAuth(object):
    def __init__(self):
        pass

    @staticmethod
    def add_user(user):
        start = millis()
        aa_request = requests.post(aa_url + '/user', data=str(user.id))
        print 'add user ' + str(millis() - start) + ' sec'
        aa_response = json.JSONDecoder().decode(aa_request.text)
        if aa_request.status_code != 200 or aa_response['success'] is False:
            return None

        return aa_response

    @staticmethod
    def delete_user(user):
        aa_request = requests.delete(aa_url + '/user/' + str(user.id))
        aa_response = json.JSONDecoder().decode(aa_request.text)
        if aa_response['success'] is False:
            return None

        return aa_response

    @staticmethod
    def add_attr(user, attr, current_user):
        start = millis()
        aa_request = requests.put(aa_url + '/user/' + str(user.id) + '/attribute/' + attr.name)
        print 'add attr ' + str(millis() - start) + ' sec'
        aa_response = json.JSONDecoder().decode(aa_request.text)
        if aa_request.status_code != 200 or aa_response['success'] is False:
            return None

        if not AttrAuth.update_key(user, current_user):
            # TODO: error handling
            return None

        return aa_response

    @staticmethod
    def delete_attr(user, attr, current_user):
        start = millis()
        aa_request = requests.delete(aa_url + '/user/' + str(user.id) + '/attribute/' + attr.name)
        print 'delete attr ' + str(millis() - start) + ' sec'
        aa_response = json.JSONDecoder().decode(aa_request.text)
        if aa_response['success'] is False and 'attributeExists' not in aa_response:
            return None

        if not AttrAuth.update_key(user, current_user):
            # TODO: error handling
            return None

        return aa_response

    @staticmethod
    def update_key(user, current_user):
        start = millis()
        # retrieve secret key from AA first
        # TODO: store the key to prevent grabing it every time
        aa_key_request = AttrAuth.get_priv_key(user)
        if aa_key_request is None:
            # TODO: real error handling
            return False

        # and submit it to the key exchange service
        params = {'email': user.email, 'secret_key': aa_key_request['privatekey']}
        print params
        kex_request = requests.post(kex_url + '/keys?access_token=' + current_user.kex_access_token, json.dumps(params))
        print 'update key ' + str(millis() - start) + ' sec'
        if kex_request.status_code != 200:
            # TODO: real error handling
            return False

        return True

    @staticmethod
    def get_priv_key(user):
        aa_request = requests.get(aa_url + '/user/' + str(user.id))
        aa_response = json.JSONDecoder().decode(aa_request.text)
        if aa_response['success'] is False or 'privatekey' not in aa_response:
            return None

        return aa_response

    @staticmethod
    def encrypt_container(container, aa_param):
        start = millis()
        print aa_param
        aa_request = requests.post(aa_url + '/encrypt/' + str(container.id), data=json.JSONEncoder().encode(aa_param))
        print 'encrypt ' + str(millis() - start) + ' sec'
        aa_response = json.JSONDecoder().decode(aa_request.text)
        if aa_response['success'] is False:
            return None

        return aa_response

    @staticmethod
    def status_container(container):
        aa_request = requests.get(aa_url + '/encrypt/' + str(container.id))
        aa_response = json.JSONDecoder().decode(aa_request.text)

        return aa_response

    @staticmethod
    def decrypt_container(data):
        start = millis()
        print data
        aa_request = requests.post(aa_url + '/decrypt/' + str(1), data=data)
        print 'decrypt ' + str(millis() - start) + ' sec'
        aa_response = json.JSONDecoder().decode(aa_request.text)

        return aa_response
