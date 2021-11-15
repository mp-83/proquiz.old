import os
import sys
import transaction
from pyramid.config import Configurator
from pyramid.response import Response
from pyramid.session import SignedCookieSessionFactory
from pyramid.paster import get_appsettings, setup_logging
from sqlalchemy import create_engine
from codechallenge.models import Question, DBSession, Base


def init_db(engine):
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
    # with transaction.manager:
    #     model = Page(title='Root', body='<p>Root</p>')
    #     DBSession.add(Question)


def main(global_config, **settings):
    db_uri = '{sql_protocol}://{user}:{pwd}@{host}/{db}?charset=utf8mb4'.format(
        sql_protocol=os.getenv('SQL_PROTOCOL'),
        user=os.getenv('MYSQL_USER'),
        pwd=os.getenv('MYSQL_PASSWORD'),
        host=os.getenv('MYSQL_HOST'),
        db=os.getenv('MYSQL_DATABASE')
    )
    engine = create_engine(db_uri)
    init_db(engine)
    
    session_factory = SignedCookieSessionFactory('sessionFactory')
    config = Configurator(
        settings=settings,
        session_factory=session_factory,
        root_factory='codechallenge.models.Root'
    )
    config.include('pyramid_jinja2')    
    config.add_route('start', '/')
    config.add_route('question', '/question')
    config.add_static_view(name='static', path='codechallenge:static')
    config.scan('.views')
    return config.make_wsgi_app()
