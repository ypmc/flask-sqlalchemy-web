import functools
import random
import time
import os
import flask_login
from flask import Flask, redirect, url_for, request, render_template, make_response, abort, jsonify
from flask_login import LoginManager

import json

import monitor_logger
import monitor_util
import monitor_db

# from werkzeug.utils import secure_filename

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
# login_manager.login_message = 'please login!'
login_manager.session_protection = 'strong'
logger = monitor_logger.get_logger(__name__)

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
UPLOAD_PATH = 'upload'


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


# http://flask.pocoo.org/docs/0.12/patterns/fileuploads/
@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            logger.debug('No file part')
            return jsonify({'code': -1, 'filename': '', 'msg': 'No file part'})
        file = request.files['file']
        # if user does not select file, browser also submit a empty part without filename
        if file.filename == '':
            logger.debug('No selected file')
            return jsonify({'code': -1, 'filename': '', 'msg': 'No selected file'})
        else:
            try:
                if file and allowed_file(file.filename):
                    origin_file_name = file.filename
                    logger.debug('filename is %s' % origin_file_name)
                    # filename = secure_filename(file.filename)
                    filename = origin_file_name

                    if os.path.exists(UPLOAD_PATH):
                        logger.debug('%s path exist' % UPLOAD_PATH)
                        pass
                    else:
                        logger.debug('%s path not exist, do make dir' % UPLOAD_PATH)
                        os.makedirs(UPLOAD_PATH)

                    file.save(os.path.join(UPLOAD_PATH, filename))
                    logger.debug('%s save successfully' % filename)
                    return jsonify({'code': 0, 'filename': origin_file_name, 'msg': ''})
                else:
                    logger.debug('%s not allowed' % file.filename)
                    return jsonify({'code': -1, 'filename': '', 'msg': 'File not allowed'})
            except Exception as e:
                logger.debug('upload file exception: %s' % e)
                return jsonify({'code': -1, 'filename': '', 'msg': 'Error occurred'})
    else:
        return jsonify({'code': -1, 'filename': '', 'msg': 'Method not allowed'})


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/delete', methods=['GET'])
def delete_file():
    if request.method == 'GET':
        filename = request.args.get('filename')
        timestamp = request.args.get('timestamp')
        logger.debug('delete file : %s, timestamp is %s' % (filename, timestamp))
        try:
            fullfile = os.path.join(UPLOAD_PATH, filename)

            if os.path.exists(fullfile):
                os.remove(fullfile)
                logger.debug("%s removed successfully" % fullfile)
                return jsonify({'code': 0, 'msg': ''})
            else:
                return jsonify({'code': -1, 'msg': 'File not exist'})

        except Exception as e:
            logger.debug("delete file error %s" % e)
            return jsonify({'code': -1, 'msg': 'File deleted error'})

    else:
        return jsonify({'code': -1, 'msg': 'Method not allowed'})


@app.route('/add', methods=['POST'])
def add_monitor():
    if request.method == 'POST':
        logger.debug('form data is : %s' % request.form)
        try:
            # # if request data is 'application/x-www-form-urlencoded'
            # monitor_util.add_monitor(request.form)
            # if request data is 'application/json'
            monitor_util.add_monitor(request.get_data())
            # monitor_util.add_monitor(request.data)
            return jsonify({'code': 0, 'msg': ''})
        except Exception as e:
            logger.debug("add monitor error %s" % e)
            return jsonify({'code': -1, 'msg': 'Add monitor error'})
    else:
        return jsonify({'code': -1, 'msg': 'Method not allowed'})


app.secret_key = 'aHR0cDovL3d3dy53YW5kYS5jbi8='

if __name__ == '__main__':
    # print(type(flask_db.get_user('admin')))
    # print(flask_db.get_user('admin'))
    app.run(port=9000)
