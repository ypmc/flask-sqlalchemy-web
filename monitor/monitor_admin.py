from flask import Blueprint, render_template, jsonify
import monitor_logger
import time

# https://spacewander.github.io/explore-flask-zh/7-blueprints.html
# http://flask.pocoo.org/docs/0.12/blueprints/
admin = Blueprint('admin', __name__, template_folder='admin')

logger = monitor_logger.get_logger(__name__)


@admin.route('/admin/<page>')
def admin_url(page):
    logger.debug('admin page is %s' % page)
    return render_template('/admin/%s.html' % page)


@admin.route('/admin/<int:num>')
def get(num):
    logger.debug('get method is %s' % num)
    return jsonify({'value': num + 1, 'timestamp': time.time()})
