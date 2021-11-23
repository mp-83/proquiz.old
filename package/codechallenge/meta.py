import os
from pyramid.authorization import Allow, Everyone
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, Session
from sqlalchemy.schema import MetaData


NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}


DB_DSN = '{sql_protocol}://{user}:{pwd}@{host}/{db}?charset=utf8mb4'.format(
    sql_protocol=os.getenv('SQL_PROTOCOL'),
    user=os.getenv('MYSQL_USER'),
    pwd=os.getenv('MYSQL_PASSWORD'),
    host=os.getenv('MYSQL_HOST'),
    db=os.getenv('MYSQL_DATABASE')
)


cache = {}
metadata = MetaData(naming_convention=NAMING_CONVENTION)
Base = declarative_base(metadata=metadata)



def get_engine():
    echo = True
    db_uri = DB_DSN
    if os.getenv('TESTING'):
        echo = False
        db_uri = 'sqlite:///:memory:'
        
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
