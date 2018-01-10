import flask_login
from flask import Flask, session, redirect, url_for, escape, request, render_template, make_response, jsonify
import logging
import sys
import os
from flask_login import LoginManager

login_manager = LoginManager()

app = Flask(__name__)
login_manager.init_app(app)

# 获取logger实例，如果参数为空则返回root logger
logger = logging.getLogger(__name__)
LOG_PATH = 'logs'
LOG_FILE = 'text.txt'


def config():
    if os.path.exists(LOG_PATH):
        pass
    else:
        os.mkdir(LOG_PATH)
    # 指定logger输出格式
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s')
    # 文件日志
    file_handler = logging.FileHandler("%s/%s" % (LOG_PATH, LOG_FILE))
    file_handler.setFormatter(formatter)  # 可以通过setFormatter指定输出格式
    # 控制台日志
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.formatter = formatter  # 也可以直接给formatter赋值
    # 为logger添加的日志处理器，可以自定义日志处理器让其输出到其他地方
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    # 指定日志的最低输出级别，默认为WARN级别
    logger.setLevel(logging.DEBUG)


@app.route('/', methods=['GET', 'POST'])
@flask_login.login_required
def index():
    logger.debug("index page")
    logger.debug("cookie name %s" % request.cookies.get('username'))

    if 'username' in session:
        logger.debug("login user is %s" % flask_login.current_user)
        logger.debug('Logged in as %s' % escape(session['username']))
        return render_template('index.html', name=session['username'])
    else:
        logger.debug("you are not logged in")
        return render_template('login.html')


@app.route('/error')
def error():
    logger.debug("error page")
    return render_template('error.html')


class User(flask_login.UserMixin):
    pass


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        logger.debug("login post method")
        username = request.form['username']
        password = request.form['password']

        if username == 'admin' and password == 'admin123':
            user = User()
            flask_login.login_user(user)
            user.id = "admin"
            user.is_authenticated = True
            flask_login.login_user(user)
            session['username'] = username
            session['password'] = password
            resp = make_response(render_template('index.html', name=username))
            resp.set_cookie('username', username)
            # return resp
            return jsonify({'status': '0', 'errmsg': '登录成功！'})
        else:
            # return redirect(url_for('error'))
            return jsonify({'status': '-1', 'errmsg': '用户名或密码错误！'})

    logger.debug("login get method")
    return render_template('login.html')


@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    logger.debug("logout page")
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/hello')
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('index.html', name=name)


@app.route('/json')
def json():
    return jsonify({'username': session['username'], 'password': session['password']})


# set the secret key.  keep this really secret:
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

if __name__ == '__main__':
    config()
    app.run(port=9000)
