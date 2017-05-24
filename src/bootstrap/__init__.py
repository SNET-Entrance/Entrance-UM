import os
from const import basedir
from flask import Flask
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_user import SQLAlchemyAdapter, UserManager
from flask_user.signals import user_registered
from flask_login import LoginManager
from flask_cache import Cache
from flask_bootstrap import Bootstrap

import jinja2

app = Flask(__name__)
my_loader = jinja2.ChoiceLoader([
    app.jinja_loader,
    jinja2.FileSystemLoader('at/templates'),
])
app.jinja_loader = my_loader

# load config files
# load production config when deploying component on server
app.config.from_object('config.default')
# app.config.from_object('config.production')

# define shortened globals
aa_url = app.config['ATTRIBUTE_AUTHORITY_URL']
kex_url = app.config['KEY_EXCHANGE_URL']
umcm_client_id = app.config['UMCM_CLIENT_ID']
umcm_client_secret = app.config['UMCM_CLIENT_SECRET']
cont_ext = app.config['CONTAINER_EXTENSION']
all_attr = app.config['ALL_ATTRIBUTE']
policy_mode = app.config['POLICY_MODE']

# initialize sqlalchemy, flask-user, etc.
db = SQLAlchemy(app)
mail = Mail(app)
Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)

# Initialize Cache
app.cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# initialize components
from models import User

db_adapter = SQLAlchemyAdapter(db, User)
user_manager = UserManager(db_adapter=db_adapter, app=app, login_manager=login_manager)

import views

from um import um

app.register_blueprint(um)

from cm import cm

app.register_blueprint(cm)

from at import at

app.register_blueprint(at)

from fit import fit

app.register_blueprint(fit)

from fexplorer import fexplorer

app.register_blueprint(fexplorer)

import oauth


from um import models

# this handler creates a directory for every registered user
@user_registered.connect_via(app)
def _after_registration_hook(sender, user, **extra):
    user_dir = os.path.join(basedir, 'data', str(user.id))
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)

    attr_all = models.Attribute(all_attr, True, user.id)
    db.session.add(attr_all)
    db.session.commit()
    db.session.flush()

