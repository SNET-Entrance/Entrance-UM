import uuid

from bootstrap import db, all_attr, policy_mode
from bootstrap.models import Ext, AttrAuth
from um.models import Contact, Attribute


class Container(db.Model, Ext):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)  # name of the container
    path = db.Column(db.Text, nullable=False)  # path to the container file
    type = db.Column(db.Integer, nullable=False)  # used by the policy enforcement strategies
    files = db.relationship('File', backref='container', cascade='all, delete-orphan', lazy='joined')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __init__(self, name, path, type, user_id):
        self.name = name
        self.path = path
        self.type = type
        self.user_id = user_id

    # reencrypts a container considering the new attributes sets of contacts
    # called whenever a contact is modified
    def reencrypt(self, user):
        container = Container(self.name, self.path, self.type, user.id)
        container.files = self.files
        for f in container.files:
            f.policy = Policy.generate(f.policy_text, user)
            db.session.add(f)
        db.session.delete(self)
        db.session.add(container)
        db.session.commit()

        out = container.dict()
        out['files'] = list()
        for f in container.files:
            out['files'].append(f.dict())

        aa_param = dict()
        aa_param['files'] = list()
        for f in out['files']:
            aa_param['files'].append({
                "path": f['path'],
                "type": f['type'],
                "policy": f['policy']
            })
        aa_param['outfile'] = container.path
        aa_param['overwriteOutfile'] = True

        aa_response = AttrAuth.encrypt_container(container, aa_param)
        if aa_response is None:
            return None

        return True


class File(db.Model, Ext):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    path = db.Column(db.Text, nullable=False)  # path to the file
    type = db.Column(db.Text, nullable=False)  # always PABE14
    policy = db.Column(db.Text, nullable=False)  # the actual ABE policy
    policy_text = db.Column(db.Text, nullable=False)  # the specified policy of the user
    container_id = db.Column(db.Integer, db.ForeignKey('container.id'))

    def __init__(self, path, type, policy, policy_text, container_id):
        self.path = path
        self.type = type
        self.policy = policy
        self.policy_text = policy_text
        self.container_id = container_id


class Policy(object):
    def __init__(self):
        pass

    @staticmethod
    def evaluate(policy, user):
        operators = ['<', '>', '=', '<=', '>=']  # list of operators to identify and evaluate numeric attributes
        users = Contact.query.filter_by(user_id=user.id).all()  # load all contacts of a user
        literals = [x.split(':') for x in policy.split(',')]  # parse submitted policy
        excludes = set(
                [x[0].replace('NOT ', '') for x in literals if x[0].startswith('NOT ')])  # identify explicit excludes

        allowed_users = []  # initialize the authorized set of contacts
        for user in users:  # iterate over users list
            attrs = set([a.display_name for a in user.attributes])  # extract attributes
            for literal in literals:  # for each user iterate through literals
                if any(any(x in s for s in literal) for x in operators):  # if any literal has an operator
                    condition = True
                    for l in literal:
                        operator = ''
                        for o in operators:
                            if o in l:
                                operator = o
                        if operator == '':
                            if l not in attrs:
                                condition = False
                                continue
                            else:
                                continue

                        attr, cond = l.split(operator)
                        present = False
                        for a in attrs:
                            if attr in a:
                                present = True
                                value = a.split('=')[1]
                                if not eval(
                                                        value + operator + cond):  # check if the literal is met by the contact's attribute value
                                    condition = False
                        if not present:
                            condition = False

                    if condition:  # if condition is met check if user is in exclude list
                        if len(excludes.intersection(attrs)) == 0:
                            allowed_users.append(user)
                else:  # if no numeric attribute is used in literals
                    if set(literal).issubset(attrs):  # simply check if attributes set of contact is subset of literals
                        if len(excludes.intersection(
                                attrs)) == 0:  # and ensure again that contact is not in exclude list
                            allowed_users.append(user)

        return list(set([a for a in allowed_users]))  # return a distinct set of authorized contacts

    @staticmethod
    def convert(policy):
        # convert a policy into an actual ABE policy
        return ' OR '.join(['(' + ' AND '.join(l) + ')' for l in [x.split(':') for x in policy.split(',')]])

    @staticmethod
    def generate(policy, current_user):
        # generate a policy based on a user-specified policy dependend on the policy_mode
        if policy == all_attr:  # if policy is the default policy simply use it
            return policy
        else:
            # otherwise ...
            users = Policy.evaluate(policy, current_user)  # compute the authorized set of contacts
            if policy_mode == 0:
                if 'NOT' not in policy:  # normal ABE only work if no excludes have been used
                    return Policy.convert(policy)
                    # TODO: else case - what to do if exlcuded have been used
            elif policy_mode == 1:  # case: static ciphertext strategy
                uuid_attr = 'AAAAA' + str(uuid.uuid4()).replace('-', '')  # generate a unique attribute
                attr = Attribute(uuid_attr, True, current_user.id)  # store this attribute permanently
                db.session.add(attr)
                db.session.commit()

                # and assign it to the authorized contacts
                for user in users:
                    user.attributes.append(attr)
                    db.session.add(user)
                    aa_response = AttrAuth.add_attr(user, attr, current_user)  # AA communication
                    if aa_response is None:
                        db.session.rollback()
                db.session.commit()
                return uuid_attr
            elif policy_mode == 2:  # case: static secret key strategy
                return ' OR '.join([c.identity for c in
                                    users])  # generate disjunction of identity attribute of authorized contacts

    @staticmethod
    def check_for(contact, user):
        # check_for() is used to determine ciphertexts that have to be updated after a contact has been modified
        container = Container.query.filter_by(user_id=user.id)
        for c in container:  # iterate over all container of a user
            if c.type == 0:  # case: no strategy used - do nothing
                pass
            elif c.type == 1:  # case: static ciphertext strategy used
                for f in c.files:  # iterate over all files - for each file
                    allowed_users = Policy.evaluate(f.policy_text, user)  # evaluate the policy of the file
                    uuid = Attribute.query.filter_by(name=f.policy).first()
                    if contact not in allowed_users and uuid in contact.attributes:  # if contact is not in set of allowed_users after modification
                        contact.attributes.remove(uuid)  # remove uuid attribute from the contact
                        db.session.add(contact)
                        db.session.commit()
                        aa_response = AttrAuth.delete_attr(contact, uuid, user)  # inform AA
                        if aa_response is None:
                            db.session.rollback()
                    elif contact in allowed_users and uuid not in contact.attributes:  # if contact is in set of allowed_users but has not the corresponding attribute
                        contact.attributes.append(uuid)  # assign attribute to the contact
                        db.session.add(contact)
                        db.session.commit()
                        aa_response = AttrAuth.add_attr(contact, uuid, user)  # inform AA
                        if aa_response is None:
                            db.session.rollback()
            elif c.type == 2:  # case: static secret key strategy used
                for f in c.files:  # iterate through files again
                    allowed_users = Policy.evaluate(f.policy_text, user)  # compute authorized users
                    if contact not in allowed_users and contact.identity in f.policy:  # if user is not intented to have access to the resource after modification
                        c.reencrypt(user)  # reencrypt
                    if contact in allowed_users and contact.identity not in f.policy:  # if user is intended to have access to the resource after the modification
                        c.reencrypt(user)  # reencrypt

                        # TODO: make this easier
