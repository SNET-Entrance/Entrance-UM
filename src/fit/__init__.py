from flask import Blueprint

fit = Blueprint('fit', __name__, static_folder='static', template_folder='templates', url_prefix='/fitness')

import views