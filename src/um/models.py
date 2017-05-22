import uuid

from bootstrap import db
from bootstrap.models import Ext

contacts_attributes = db.Table('contacts_attributes',
    db.Column('contact_id', db.Integer, db.ForeignKey('contact.id')),
    db.Column('attribute_id', db.Integer, db.ForeignKey('attribute.id'))
)


class Contact(db.Model, Ext):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False, unique=True)
    secret_key = db.Column(db.BLOB, nullable=True) # currently not used to cache the secret key of a contact
    identity = db.Column(db.Text, nullable=False, unique=True) # unique identity attribute
    # children of a contact
    properties = db.relationship('Property', backref='owner', cascade='all, delete-orphan', lazy='joined')
    attributes = db.relationship('Attribute', secondary=contacts_attributes, backref=db.backref('owner', lazy='joined'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __init__(self, name, email, user_id):
        self.name = name
        self.email = email
        self.identity = 'AAAAA' + str(uuid.uuid4()).replace('-', '')
        self.user_id = user_id


class Property(db.Model, Ext):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    key = db.Column(db.Text, nullable=False)
    value = db.Column(db.Text, nullable=False)
    contact_id = db.Column(db.Integer, db.ForeignKey('contact.id'))

    def __init__(self, key, value, contact_id):
        self.key = key
        self.value = value
        self.contact_id = contact_id


class Attribute(db.Model, Ext):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False, unique=True) # actual ABE attribtue - not whitespaces
    display_name = db.Column(db.Text, nullable=False) # actual user input
    sys = db.Column(db.Boolean, nullable=False) # attribute with this set to True are not diplayed to users
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    activityDateTime = db.Column(db.Text, nullable=False, unique=True)

    def __init__(self, display_name, sys, user_id, activityDateTime):
        self.name = display_name.replace(' ', '_') # name is automatically generated
        self.display_name = display_name
        self.sys = sys
        self.user_id = user_id
        self.activityDateTime =activityDateTime