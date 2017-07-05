import datetime
from const import basedir
import os

# create required paths on the file system
if not os.path.exists(basedir):
    os.makedirs(basedir)
    os.makedirs(os.path.join(basedir, 'data'))
    os.makedirs(os.path.join(basedir, 'fitness'))
    os.makedirs(os.path.join(basedir, 'fitness', 'tmp'))

# create database files
open(basedir + 'entrance.db', 'w')
open(basedir + 'entrance.dev.db', 'w')
open(basedir + 'entrance.test.db', 'w')

from bootstrap import db, all_attr
from bootstrap.models import Client, User

db.create_all()  # initialize databases

# register the Windows 10 Client application
# to enable OAuth authentication
windows_client = Client(
    name='entrance Windows 10 App',
    description='Windows 10 Client Application of entrance',
    client_id='voUmLYgFOE2GlNQqrcBelKEuSCGQ6zWQZVsPKZM9',
    client_secret='09Nlj1XI11MgTeJwOJ3Dmy48jZMVsWvgHSuTV03Xdl6dKYoDZs',
    is_confidential=True,
    _redirect_uris='/',
    _default_scopes=''
)
db.session.add(windows_client)
db.session.commit()

user = User(
    username='philip',
    password='$2a$12$Ou1onuD8TtnkyyKsDr7JPe53sabvcKElgd5La9DWUOBKrYDbk.jCy',
    email='philip.raschke@outlook.com',
    confirmed_at=datetime.datetime.now(),
    logged_in_edugain=False,
    active=True,
    pages='[{"widgets": [], "name": "My Dashboard", "slug": "my-dashboard"}]'
)
db.session.add(user)

user2 = User(
    username='Testuser',
    password='$2a$12$jhEA1aE3Vchn1DIOfK2Dien8HEVooaMMMBjd.VgJv3Pl6HVq1X62S',
    email='test@notavailable.org',
    confirmed_at=datetime.datetime.now(),
    logged_in_edugain=False,
    active=True,
    pages='[{"widgets": [], "name": "My Dashboard", "slug": "my-dashboard"}]'
)
db.session.add(user2)

user3 = User(
    username='dthatmann',
    password='$2a$12$jhEA1aE3Vchn1DIOfK2Dien8HEVooaMMMBjd.VgJv3Pl6HVq1X62S',
    email='d.thatmann@tu-berlin.de',
    confirmed_at=datetime.datetime.now(),
    logged_in_edugain=False,
    active=True,
    pages='[{"widgets": [], "name": "My Dashboard", "slug": "my-dashboard"}]'
)
db.session.add(user3)

user4 = User(
    username='jduver',
    password='$2a$12$jhEA1aE3Vchn1DIOfK2Dien8HEVooaMMMBjd.VgJv3Pl6HVq1X62S',
    email='jonas.duever@campus.tu-berlin.de',
    confirmed_at=datetime.datetime.now(),
    logged_in_edugain=False,
    active=True,
    pages='[{"widgets": [], "name": "My Dashboard", "slug": "my-dashboard"}]'
)
db.session.add(user4)

user5 = User(
    username='iwailo',
    password='$2a$12$jhEA1aE3Vchn1DIOfK2Dien8HEVooaMMMBjd.VgJv3Pl6HVq1X62S',
    email='iwailo.denisow@campus.tu-berlin.de',
    confirmed_at=datetime.datetime.now(),
    logged_in_edugain=False,
    active=True,
    pages='[{"widgets": [], "name": "My Dashboard", "slug": "my-dashboard"}]'
)
db.session.add(user5)

db.session.commit()

from um import models

attr_all = models.Attribute(all_attr, True, user.id,'')
db.session.add(attr_all)
db.session.commit()
#db.session.flush()