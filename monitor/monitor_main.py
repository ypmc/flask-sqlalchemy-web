import functools
import random
import time

import flask_login
from flask import Flask, redirect, url_for, request, render_template, make_response, abort, jsonify
from flask_login import LoginManager

import json

import monitor_logger
import monitor_util
import monitor_db

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'please login!'
login_manager.session_protection = 'strong'
logger = monitor_logger.get_logger(__name__)


# http://www.pythondoc.com/flask-login/index.html#request-loader
# http://docs.jinkan.org/docs/flask/index.html
# http://flask-login.readthedocs.io/en/latest/#login-example
class User(flask_login.UserMixin):
    pass


def log(*text):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            logger.debug('执行方法：%s，请求参数：%s():' % (func.__name__, text))
            return func(*args, **kw)

        return wrapper

    return decorator


@login_manager.user_loader
def user_loader(username):
    user = User()
    user.id = username
    logger.debug("user_loader user is %s, is_authenticated %s" % (user.id, user.is_authenticated))
    return user


# 使用request_loader的自定义登录, 同时支持url参数和和使用Authorization头部的基础认证的登录：
@login_manager.request_loader
def request_loader(req):
    logger.debug("request_loader url is %s, request args is %s" % (req.url, req.args))
    authorization = request.headers.get('Authorization')
    logger.debug("Authorization is %s" % authorization)
    # 模拟api登录
    if authorization:
        # get user from authorization
        user = User()
        user.id = 'admin'
        logger.debug("user is %s" % user)
        return user
    return None


@log
def is_safe_url(next_url):
    logger.debug("next url is %s:" % next_url)
    return True


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@flask_login.login_required
def index():
    logger.debug("index page, method is %s" % request.method)
    return render_template('index.html', name=flask_login.current_user.id)


@app.route('/error')
@app.errorhandler(400)
@app.errorhandler(401)
@app.errorhandler(500)
def error(e):
    logger.debug("error occurred: %s" % e)
    try:
        code = e.code
        if code == 400:
            return render_template('400.html')
        elif code == 401:
            return render_template('401.html')
        else:
            return render_template('error.html')
    except Exception as e:
        logger.debug('exception is %s' % e)
    finally:
        return render_template('error.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        logger.debug("login post method")
        username = request.form['username']
        password = request.form['password']

        user = monitor_db.get_user_session(username)
        logger.debug('db user id is %s, detail is %s' % (user.username, user))

        next_url = request.args.get("next")
        logger.debug('next is %s' % next_url)

        if password == 'admin123' and username == user.username:
            # set login user
            user = User()
            user.id = username
            flask_login.login_user(user)

            resp = make_response(render_template('index.html', name=username))
            resp.set_cookie('username', username)
            if not is_safe_url(next_url):
                return abort(400)
            return redirect(next_url or url_for('index'))
        else:
            return abort(401)

    logger.debug("login get method")
    return render_template('login.html')


@app.route('/logout')
@flask_login.login_required
def logout():
    # remove the username from the session if it's there
    logger.debug("logout page")
    flask_login.logout_user()
    return redirect(url_for('login'))


@app.route('/detail')
@flask_login.login_required
def detail():
    return render_template('detail.html')


@app.route('/api', methods=['GET'])
@flask_login.login_required
def api():
    return jsonify({'value': random.random(), 'timestamp': int(time.time())})


@app.route('/api/list', methods=['GET'])
def get_list():
    page = request.args.get('page')
    limit = request.args.get('limit')
    logger.debug("get_list: page = %s, limit = %s" % (page, limit))
    pages = monitor_util.get_monitor_flask_sqlalchemy(int(page), int(limit))
    if pages is None:
        return jsonify({"code": 0, "msg": "", "count": 0, "data": {}})
    else:
        data = []
        for item in pages.items:
            item.__dict__['_sa_instance_state'] = ''
            item.__dict__['create_time'] = "%s" % item.__dict__['create_time']
            item.__dict__['monitor_time'] = "%s" % item.__dict__['monitor_time']
            data.append(item.__dict__)
        result = json.dumps({"code": 0, "msg": "", "count": pages.total, "data": data})
        return result


app.secret_key = 'aHR0cDovL3d3dy53YW5kYS5jbi8='

if __name__ == '__main__':
    # print(type(flask_db.get_user('admin')))
    # print(flask_db.get_user('admin'))
    app.run(port=9000)
