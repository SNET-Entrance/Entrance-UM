from flask import Blueprint

# initialization of the blueprint
um = Blueprint('um', __name__, static_folder='static', template_folder='templates', url_prefix='/contacts')

import views