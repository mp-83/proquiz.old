import os
from pyramid.authorization import Allow, Everyone
from sqlalchemy import Column, Integer, String, select, create_engine
from sqlalchemy.orm import declarative_base, Session


cache = {}
Base = declarative_base()


def my_sql_dsn():
    return '{sql_protocol}://{user}:{pwd}@{host}/{db}?charset=utf8mb4'.format(
        sql_protocol=os.getenv('SQL_PROTOCOL'),
        user=os.getenv('MYSQL_USER'),
        pwd=os.getenv('MYSQL_PASSWORD'),
        host=os.getenv('MYSQL_HOST'),
        db=os.getenv('MYSQL_DATABASE')
    )


def get_engine():
    echo = True
    if os.getenv('TESTING'):
        echo = False
        db_uri = 'sqlite:///:memory:'
    else:
        db_uri = my_sql_dsn()
        
    if not cache.get('engine'):
        cache['engine'] = create_engine(db_uri, echo=echo)
    return cache['engine']


def init_session():
    engine = get_engine() 
    DBSession = Session(engine)
    return DBSession


def init_db():
    Base.metadata.create_all(get_engine())


class Root:
    __acl__ = [(Allow, Everyone, 'view'),
               (Allow, 'group:editors', 'edit')]

    def __init__(self, request):
        pass
