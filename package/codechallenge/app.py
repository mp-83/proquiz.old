import logging

import os
import sys
from pyramid.config import Configurator
from pyramid.response import Response
from pyramid.session import SignedCookieSessionFactory
from pyramid.paster import get_appsettings, setup_logging


logger = logging.getLogger(__name__)


DB_DSN = '{sql_protocol}://{user}:{pwd}@{host}/{db}?charset=utf8mb4'.format(
    sql_protocol=os.getenv('SQL_PROTOCOL'),
    user=os.getenv('MYSQL_USER'),
    pwd=os.getenv('MYSQL_PASSWORD'),
    host=os.getenv('MYSQL_HOST'),
    db=os.getenv('MYSQL_DATABASE')
)


class StoreConfig:
    _instance = None
    _config = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(StoreConfig, cls).__new__(cls)
        return cls._instance

    @property
    def config(self):
        return self._config
        
    @config.setter
    def config(self, value):
        self._config = value

    @property
    def session(self):
        factory = self.config['dbsession_factory']
        return factory()
        

def main(global_config, **settings):
    settings['sqlalchemy.url'] = DB_DSN
    session_factory = SignedCookieSessionFactory('sessionFactory')
    config = Configurator(
        settings=settings,
        session_factory=session_factory,
        root_factory='codechallenge.models.meta.Root'
    )
    config.include('pyramid_jinja2')    
    config.add_route('start', '/')
    config.add_route('question', '/question')
    config.add_static_view(name='static', path='codechallenge:static')
    config.scan('.views')
    config.include('codechallenge.models.meta')
    
    StoreConfig().config = config
    return config.make_wsgi_app()
