from flask import Blueprint

# initialize the blueprint
cm = Blueprint('cm', __name__, static_folder='static', template_folder='templates', url_prefix='/container')

import views