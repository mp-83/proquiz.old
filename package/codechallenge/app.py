from pyramid.config import Configurator
from pyramid.response import Response
from pyramid.session import SignedCookieSessionFactory


def main(global_config, **settings):
    session_factory = SignedCookieSessionFactory('sessionFactory')
    config = Configurator(settings=settings, session_factory=session_factory)
    config.include('pyramid_jinja2')    
    config.add_route('start', '/')
    config.add_route('question', '/question')
    config.add_static_view(name='static', path='codechallenge:static')
    config.scan('.views')
    return config.make_wsgi_app()
