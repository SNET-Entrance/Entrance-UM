from flask import Blueprint

fexplorer = Blueprint('fexplorer', __name__, static_folder='static', template_folder='templates', url_prefix='/files')

import views