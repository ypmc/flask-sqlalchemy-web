from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


# http://docs.sqlalchemy.org/en/latest/orm/mapping_columns.html
class User(Base):
    __tablename__ = 't_user'

    id = Column('id', Integer, primary_key=True)
    username = Column('user_id', String(128))
    email = Column('email', String(128))
    password = Column('pwd_hash', String(128))
    create_time = Column('create_time', String(128))
    update_time = Column('update_time', String(128))

    def __init__(self, id, username, email, password, create_time, update_time):
        self.id = id
        self.username = username
        self.email = email
        self.password = password
        self.create_time = create_time
        self.update_time = update_time

    def __repr__(self):
        return '<id is %s, username is %s, password is %s, email is %s, create time is %s, update time is %s>' % (
            self.id, self.username, self.password, self.email, self.create_time, self.update_time)
