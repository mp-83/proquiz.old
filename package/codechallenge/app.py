from pyramid.config import Configurator
from pyramid.response import Response


def main(global_config, **settings):
    config = Configurator(settings=settings)
    config.include('pyramid_jinja2')    
    config.add_route('start', '/')
    config.add_route('question', '/question')
    config.scan('.views')
    return config.make_wsgi_app()
