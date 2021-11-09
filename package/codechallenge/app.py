from pyramid.config import Configurator
from pyramid.response import Response


def main(global_config, **settings):
    config = Configurator(settings=settings)
    config.include('pyramid_chameleon')    
    config.add_route('home', '/')
    config.add_route('test', '/test')
    config.scan('.views')
    return config.make_wsgi_app()
