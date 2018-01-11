import json
import random

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import select

import monitor_db
import monitor_logger
import monitor_util

Base = declarative_base()

url = 'mysql+mysqlconnector://hawkeye:Hawkeye#Pwd123@10.214.168.25:3306/wingx_hawkeye'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

logger = monitor_logger.get_logger(__name__)


# http://flask-sqlalchemy.pocoo.org/2.3/
# http://docs.sqlalchemy.org/en/latest/
# SQLAlchemy orm
class Monitor(Base):
    __tablename__ = 't_credit_monitor'

    id = Column('id', Integer, primary_key=True)
    credit_type = Column('credit_type', String(128))
    query_type = Column('query_type', String(128))
    credit_status = Column('credit_status', String(128))
    monitor_time = Column('monitor_time', String(128))
    elapsed_time = Column('elapsed_time', String(128))
    create_time = Column('create_time', String(128))

    def __init__(self, id, credit_type, query_type, credit_status, monitor_time, elapsed_time, create_time):
        self.id = id
        self.credit_type = credit_type
        self.query_type = query_type
        self.credit_status = credit_status
        self.monitor_time = monitor_time
        self.elapsed_time = elapsed_time
        self.create_time = create_time

    def __repr__(self):
        return '<id is %s, creditType is %s, queryType is %s, creditStatus is %s, monitorTime is %s, elapsedTime is %s>' % (
            self.id, self.credit_type, self.query_type, self.credit_status, self.monitor_time, self.elapsed_time)


# Flask-SQLAlchemy
class FlaskMonitor(db.Model):
    __tablename__ = 't_credit_monitor'

    id = Column('id', Integer, primary_key=True)
    credit_type = Column('credit_type', String(128))
    query_type = Column('query_type', String(128))
    credit_status = Column('credit_status', String(128))
    monitor_time = Column('monitor_time', String(128))
    elapsed_time = Column('elapsed_time', String(128))
    create_time = Column('create_time', String(128))

    def __init__(self, id, credit_type, query_type, credit_status, monitor_time, elapsed_time, create_time):
        self.id = id
        self.credit_type = credit_type
        self.query_type = query_type
        self.credit_status = credit_status
        self.monitor_time = monitor_time
        self.elapsed_time = elapsed_time
        self.create_time = create_time

    def __repr__(self):
        return '<id is %s, creditType is %s, queryType is %s, creditStatus is %s, monitorTime is %s, elapsedTime is %s>' % (
            self.id, self.credit_type, self.query_type, self.credit_status, self.monitor_time, self.elapsed_time)


# SQLAlchemy core
metadata = MetaData()
T_Monitor = Table('t_credit_monitor', metadata, Column('id', Integer, primary_key=True)
                  , Column('credit_type', String(128))
                  , Column('query_type', String(128))
                  , Column('credit_status', String(128))
                  , Column('monitor_time', String(128))
                  , Column('elapsed_time', String(128))
                  , Column('create_time', String(128)))


# http://docs.sqlalchemy.org/en/latest/
# SQLAlchemy orm
def get_monitor_with_orm():
    s = monitor_db.get_connection_session(url)
    print(s.query(Monitor).limit(2).all())
    print(s.query(Monitor).first())
    print(type(s.query(Monitor)))
    print(s.query(Monitor).count())


# SQLAlchemy core
def get_monitor_with_core():
    conn = monitor_db.get_connection_with_url(url)
    sql = select([T_Monitor])
    result = conn.execute(sql)
    print(result.rowcount)
    print(type(result.fetchall()))


# using flask_sqlalchemy
def get_monitor_flask_sqlalchemy(page=1, limit=10):
    try:
        logger.debug('get_monitor_flask_sqlalchemy: page is %s, limit is %s' % (page, limit))
        return FlaskMonitor.query.paginate(page, limit)
    except Exception as e:
        logger.debug("Exception in get_monitor_flask_sqlalchemy %s" % e)
        return None


# add monitor
def add_monitor(d):
    logger.debug('add monitor is %s' % d)
    conn = monitor_db.get_connection_with_url(url)
    d = json.loads(d)
    # Content-Type: application/json
    conn.execute(T_Monitor.insert(), [{
        'credit_type': d['credit_type']
        , 'query_type': d['query_type']
        , 'credit_status': d['credit_status']
        , 'elapsed_time': int(random.random() * 100)
    }])

    # # Content-Type: application/x-www-form-urlencoded; charset=UTF-8
    # for key in d.keys():
    #     logger.debug("form data is %s" % json.loads(key))
    #     d_dict = json.loads(key)
    #     conn.execute(T_Monitor.insert(), [{
    #         'credit_type': d_dict['credit_type']
    #         , 'query_type': d_dict['query_type']
    #         , 'credit_status': d_dict['credit_status']
    #         , 'elapsed_time': int(random.random() * 100)
    #     }])


if __name__ == '__main__':
    print(get_monitor_flask_sqlalchemy(1, 2).items)
