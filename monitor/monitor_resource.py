from flask import Blueprint

monitor_resource = Blueprint('monitor_resource', __name__, static_folder='static',
                             template_folder='templates')
