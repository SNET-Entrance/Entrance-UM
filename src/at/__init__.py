from flask import Blueprint

at = Blueprint('at', __name__, static_folder='static', template_folder='templates', url_prefix='/admintool')

import views