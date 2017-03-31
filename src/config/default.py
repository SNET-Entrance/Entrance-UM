from const import basedir
import os

ATTRIBUTE_AUTHORITY_URL = 'http://localhost:8095'
KEY_EXCHANGE_URL = 'http://localhost:5001'

CONTAINER_EXTENSION = '.media'
ALL_ATTRIBUTE = 'All'

# already registered at the KEX
# used to authenticate UM/CM against KEX
UMCM_CLIENT_ID = 'QlWDSSGCCUFdD9Nupq3vA6Q7C95IQf2LjCqwBh10'
UMCM_CLIENT_SECRET = '0Bh761e9WKEPkuyxPRMChey0d2m1uVkvDn20WyDum0Bb7TGUtt'

# Policy Mode
# Normal ABE mode   :   0
# No re-encryption  :   1
# No key update     :   2
POLICY_MODE = 0

DEBUG = True
TESTING = False
SECRET_KEY = 'w\x7f\x1b\x94}S\x98\x0e\x97\xa7\xdd\xae\xe5\xcd 4\xd3\n\xfeG\xacT\xa2\xdf\xfd\xec\xbf:|N\\"'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'entrance.dev.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

USER_APP_NAME = 'entrance'
USER_AFTER_LOGIN_ENDPOINT = 'at.index'
CSRF_ENABLED = False

MAIL_USERNAME = 'entrance.project.tu@gmail.com'
MAIL_PASSWORD = 'password1'
MAIL_DEFAULT_SENDER = 'entrance.project.tu@gmail.com'
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USE_SSL = True
MAIL_USE_TLS = False

OAUTH2_PROVIDER_TOKEN_EXPIRES_IN = 31536000
