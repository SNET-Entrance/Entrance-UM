import base64
import json
import sys

from flask import request, make_response
from flask_user import login_required, current_user
from sqlalchemy import exc

from bootstrap import db, all_attr
from bootstrap.models import AttrAuth
from cm.models import Policy
from um import um, models


@um.route('', methods=['GET'])
@login_required
def show_users():
    out = list()
    for user in models.Contact.query.filter_by(user_id=current_user.id).all(): # load all contacts of a user
        tmp = user.dict()
        tmp['properties'] = [p.dict() for p in user.properties]
        tmp['attributes'] = [a.dict() for a in user.attributes if not a.sys]
        out.append(tmp)

    return make_response(json.dumps(out), 200) # and JSON serialize it


@um.route('', methods=['POST'])
@login_required
def add_user(): # this adds a new contact for a logged-in user
    data = json.JSONDecoder().decode(request.data)
    if 'name' not in data or 'email' not in data:
        return make_response('', 400) # error missing parameters

    user = models.Contact(data['name'], data['email'], current_user.id)
    db.session.add(user)
    db.session.commit() # otherwise store contact persistently

    attr_id = models.Attribute(user.identity, False, current_user.id)
    attr_id.display_name = user.name
    attr_all = models.Attribute.query.filter_by(name=all_attr).first()
    db.session.add(attr_id)
    db.session.add(attr_all)
    db.session.commit()

    user.attributes.append(attr_id) # assign identity attribute to contact
    user.attributes.append(attr_all) # assign all attribtue to contact
    db.session.add(user)
    db.session.commit()


    aa_response = AttrAuth.add_user(user) # inform AA about created user
    if aa_response is None:
        db.session.delete(user) # delete user in error case
        db.session.commit()


        return make_response('', 500)

    user.secret_key = aa_response['secretSeed'] # the AA currently responds with the secret seed not the secret key

    aa_response = AttrAuth.add_attr(user, attr_id, current_user) # inform AA about identity AA
    if aa_response is None:
        db.session.delete(attr_id) # delete it in error case
        db.session.commit()
        return make_response('', 500)

    aa_response = AttrAuth.add_attr(user, attr_all, current_user) # inform AA about all attribute
    if aa_response is None:
        db.session.delete(attr_all) # delete in error case
        db.session.commit()
        return make_response('', 500)

    return make_response(json.dumps(user.dict()), 201)


@um.route('/<user_id>', methods=['GET'])
@login_required
def show_user(user_id):
    user = models.Contact.query.filter_by(id=user_id).first_or_404()

    if user not in current_user.contacts:
        return make_response('', 403)

    out = user.dict()
    out['properties'] = [p.dict() for p in user.properties]
    out['attributes'] = [a.dict() for a in user.attributes if not a.sys]

    # load the private key from the AA
    aa_response = AttrAuth.get_priv_key(user)
    if aa_response is not None:
        out['private_key'] = aa_response['privatekey']

    return make_response(json.dumps(out), 200)


@um.route('/<user_id>/private_key', methods=['GET'])
@login_required
def download_private_key(user_id):
    # to download the private key as file
    user = models.Contact.query.filter_by(id=user_id).first_or_404()

    if user not in current_user.contacts:
        return make_response('', 403)

    aa_response = AttrAuth.get_priv_key(user)
    if aa_response is None:
        return make_response('', 400)

    response = make_response(base64.b64decode(aa_response['privatekey']))
    response.headers['Content-Disposition'] = 'attachment; filename=' + user.email + '.private_key'
    return response


@um.route('/<user_id>/secret_key', methods=['GET'])
@login_required
def get_secret_key(user_id):
    # to get the secret key in HTTP body
    user = models.Contact.query.filter_by(id=user_id).first_or_404()

    if user not in current_user.contacts:
        return make_response('', 403)

    aa_response = AttrAuth.get_priv_key(user)
    if aa_response is None:
        return make_response('', 400)

    return make_response(aa_response['privatekey'], 200)


@um.route('/<user_id>', methods=['PUT'])
@login_required
def edit_user(user_id):
    # to modify a contact
    user = models.Contact.query.filter_by(id=user_id).first_or_404()

    if user not in current_user.contacts:
        return make_response('', 403)

    data = json.JSONDecoder().decode(request.data)
    if 'name' in data and 'email' in data:
        user.name = data['name']
        user.email = data['email']
    else:
        return make_response('', 400)

    db.session.add(user)
    db.session.commit()
    return make_response(json.dumps(user.dict()), 200)


@um.route('/<user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    # to delete a contact
    user = models.Contact.query.filter_by(id=user_id).first_or_404()

    if user not in current_user.contacts:
        return make_response('', 403)

    attr_id = models.Attribute.query.filter_by(name=user.identity).first()
    aa_response = AttrAuth.delete_attr(user, attr_id, current_user)
    if aa_response is None:
        return make_response('', 500)

    aa_response = AttrAuth.delete_user(user)
    if aa_response is None:
        return make_response('', 400)

    db.session.delete(attr_id)
    db.session.delete(user)
    db.session.commit()
    return make_response('', 200)


@um.route('/<user_id>/properties', methods=['GET'])
@login_required
def show_properties(user_id):
    user = models.Contact.query.filter_by(id=user_id).first_or_404()
    if user not in current_user.contacts:
        return make_response('', 403)

    return make_response(json.dumps([p.id for p in user.properties]), 200)


@um.route('/<user_id>/properties', methods=['POST'])
@login_required
def add_property(user_id):
    user = models.Contact.query.filter_by(id=user_id).first_or_404()
    if user not in current_user.contacts:
        return make_response('', 403)

    data = json.JSONDecoder().decode(request.data)
    if 'key' not in data or 'value' not in data:
        return make_response('', 400)

    prop = models.Property(data['key'], data['value'], user_id)
    db.session.add(prop)
    db.session.commit()
    return make_response(json.dumps(prop.dict()), 201)


@um.route('/<user_id>/properties/<prop_id>', methods=['GET'])
@login_required
def show_property(user_id, prop_id):
    user = models.Contact.query.filter_by(id=user_id).first_or_404()
    if user not in current_user.contacts:
        return make_response('', 403)

    prop = models.Property.query.filter_by(id=prop_id).first_or_404()
    return make_response(json.dumps(prop.dict()), 200)


@um.route('/<user_id>/properties/<prop_id>', methods=['PUT'])
@login_required
def edit_property(user_id, prop_id):
    user = models.Contact.query.filter_by(id=user_id).first_or_404()
    if user not in current_user.contacts:
        return make_response('', 403)

    prop = models.Property.query.filter_by(id=prop_id).first_or_404()

    data = json.JSONDecoder().decode(request.data)
    if 'key' not in data or 'value' not in data:
        return make_response('', 400)

    prop.key = data['key']
    prop.value = data['value']
    db.session.add(prop)
    db.session.commit()
    return make_response(json.dumps(prop.dict()), 200)


@um.route('/<user_id>/properties/<prop_id>', methods=['DELETE'])
@login_required
def delete_property(user_id, prop_id):
    user = models.Contact.query.filter_by(id=user_id).first_or_404()
    if user not in current_user.contacts:
        return make_response('', 403)

    prop = models.Property.query.filter_by(id=prop_id).first_or_404()

    db.session.delete(prop)
    db.session.commit()
    return make_response('', 200)


@um.route('/attributes', methods=['GET'])
@login_required
def show_attributes():
    attrs = models.Attribute.query.filter_by(user_id=current_user.id, sys=False)
    return make_response(json.dumps([a.dict() for a in attrs]), 200)


@um.route('/filter/attributes', methods=['POST'])
@login_required
def filter_attributes():
    attrs = models.Attribute.query.filter(models.Attribute.display_name.like('%'+request.data+'%')).filter(models.Attribute.user_id==current_user.id).filter(models.Attribute.sys==False).all()
    return make_response(json.dumps([a.dict() for a in attrs]), 200)


@um.route('/attributes', methods=['POST'])
@login_required
def add_attribute():
    data = json.JSONDecoder().decode(request.data)
    if 'name' not in data:
        return make_response('', 400)

    attr = models.Attribute(data['name'], False, current_user.id)
    db.session.add(attr)
    try:
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        attr = models.Attribute.query.filter_by(name=data['name']).first()
        return make_response(json.dumps(attr.dict()), 409)

    return make_response(json.dumps(attr.dict()), 201)


@um.route('/attributes/<attr_id>', methods=['GET'])
@login_required
def show_attribute(attr_id):
    attr = models.Attribute.query.filter_by(id=attr_id).first_or_404()
    if attr not in current_user.attributes:
        return make_response('', 403)

    return make_response(json.dumps(attr.dict()), 200)


@um.route('/attributes/<attr_id>', methods=['PUT'])
@login_required
def edit_attribute(attr_id):
    # this tries to modify an attribute
    # all contacts that have the original attribute assigned are updated
    # therefore the original attribute is deleted from these
    # and the new attribute is assigned to these

    attr = models.Attribute.query.filter_by(id=attr_id).first_or_404()
    if attr not in current_user.attributes:
        return make_response('', 403)

    data = json.JSONDecoder().decode(request.data)
    if 'name' not in data:
        return make_response('', 400)

    attr_new = models.Attribute(data['name'], False, current_user.id)
    db.session.add(attr_new)
    try:
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        return make_response(json.dumps(attr.dict()), 409)

    users = models.Contact.query.filter(models.Contact.attributes.contains(attr)).all()
    delete_errors = list()
    create_errors = list()
    for user in users: # iterate through contacts
        aa_response = AttrAuth.delete_attr(user, attr, current_user) # delete wave
        if aa_response is None:
            delete_errors.append(user.id) # in error case remember faulty contacts

        aa_response = AttrAuth.add_attr(user, data['name'], current_user) # create wave
        if aa_response is None:
            create_errors.append(user.id) # in error case remember faulty contacts

    if len(delete_errors) == 0 and len(create_errors) == 0: # case no errors in wave
        db.session.delete(attr_new)
        db.session.commit()
        attr.name = attr_new.name
        db.session.add(attr)
        db.session.commit()
        return make_response(json.dumps(attr.dict()), 200) # success

    if len(users) == len(create_errors): # case create wave not successfull for any user
        db.session.delete(attr_new) # delete the new attribute
        db.session.commit() # at least state is consistent

    for user in users: # iterate through users again
        if user.id not in delete_errors:
            user.attributes.remove(attr) # delete old attribute for successul contacts
        if user.id not in create_errors:
            user.attributes.append(attr_new) # create new attribute for successful contacts
        db.session.add(user)
    db.session.commit()

    # leave the rest as is
    # yet notify client with status code 500
    # to indicate an error occured
    return make_response('', 500)


@um.route('/attributes/<attr_id>', methods=['DELETE'])
@login_required
def delete_attribute(attr_id):
    # to delete an attribute
    # this function will delete an attribute
    # and tries to delete if from all contacts that had it assigned to
    attr = models.Attribute.query.filter_by(id=attr_id).first_or_404()
    if attr not in current_user.attributes:
        return make_response('', 403)

    users = models.Contact.query.filter(models.Contact.attributes.contains(attr)).all()
    delete_errors = list()
    for user in users:
        aa_response = AttrAuth.delete_attr(user, attr, current_user)
        if aa_response is None:
            delete_errors.append(user.id)

    if len(delete_errors) == 0: # analogous error handling
        db.session.delete(attr)
        db.session.commit()
        return make_response('', 200)

    for user in users:
        if user.id not in delete_errors:
            user.attributes.remove(attr)
            db.session.add(user)
    db.session.commit()

    return make_response('', 500)


@um.route('/<user_id>/attributes', methods=['POST'])
@login_required
def assign_new_attribute(user_id):
    # to assign a new attribute to a contact
    user = models.Contact.query.filter_by(id=user_id).first_or_404()
    if user not in current_user.contacts:
        return make_response('', 403)

    data = json.JSONDecoder().decode(request.data)
    if 'name' not in data:
        return make_response('', 400)

    attr = models.Attribute(data['name'], False, current_user.id) # instantiate attribute
    db.session.add(attr)
    try:
        db.session.commit() # try to commit
    except exc.IntegrityError: # in case attribute already exists
        db.session.rollback()
        attr = models.Attribute.query.filter_by(display_name=data['name']).first() # use the existent one
        if attr in user.attributes: # if attribute already assigned - notify user
            return make_response('', 409)

    # else ...
    aa_response = AttrAuth.add_attr(user, attr, current_user) # inform AA
    if aa_response is None:
        db.session.delete(attr) # error case - delete attribute
        db.session.commit()
        return make_response('', 500) # and inform user

    user.attributes.append(attr) # otherwise assign it to contact
    db.session.add(user)
    db.session.commit()

    Policy.check_for(user, current_user) # depending on the enforcement strategy - reevaluate all container

    return make_response(json.dumps(attr.dict()), 200) # success


@um.route('/<user_id>/attributes/<attr_id>', methods=['POST'])
@login_required
def assign_attribute(user_id, attr_id):
    # to assign an existent attribute to a contact
    user = models.Contact.query.filter_by(id=user_id).first_or_404()
    if user not in current_user.contacts:
        return make_response('', 403)

    attr = models.Attribute.query.filter_by(id=attr_id).first_or_404()
    if attr not in current_user.attributes:
        return make_response('', 403)

    aa_response = AttrAuth.add_attr(user, attr, current_user)
    if aa_response is None:
        return make_response('', 500)

    user.attributes.append(attr)
    db.session.add(user)
    db.session.commit()

    Policy.check_for(user, current_user) # involves reevaluation

    return make_response('', 200)


@um.route('/<user_id>/attributes/<attr_id>', methods=['DELETE'])
@login_required
def dissociate_attribute(user_id, attr_id):
    # to dissociate an attribute from a contact
    # NOTE: this does not delete the entire attribute
    user = models.Contact.query.filter_by(id=user_id).first_or_404()
    if user not in current_user.contacts:
        return make_response('', 403)

    attr = models.Attribute.query.filter_by(id=attr_id).first_or_404()
    if attr not in current_user.attributes:
        return make_response('', 403)

    aa_response = AttrAuth.delete_attr(user, attr, current_user)
    if aa_response is None:
        return make_response('', 500)

    user.attributes.remove(attr)
    db.session.add(user)
    db.session.commit()

    Policy.check_for(user, current_user) # involves reevaluation

    return make_response('', 200)
