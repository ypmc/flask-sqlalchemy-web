import random
import time

from flask import jsonify
from flask_restful import Resource


# http://www.flaskapi.org/
# https://www.fullstackpython.com/api-creation.html
# 使用Flask-RESTful构建REST API
# http://flask-restful.readthedocs.io/en/latest/
# https://www.codementor.io/sagaragarwal94/building-a-basic-restful-api-in-python-58k02xsiq
class MonitorApi(Resource):
    @staticmethod
    def get(id):
        return jsonify({'id': id, 'value': random.random(), 'timestamp': int(time.time())})
