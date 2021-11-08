from pyramid.config import Configurator
from pyramid.response import Response


def good_evening(request):
    return Response('<body><h1>Good Evening y\'all !!! Does it work? It does :)</h1></body>')


def main(global_config, **settings):
    config = Configurator(settings=settings)
    config.add_route('good-evening', '/')
    config.add_view(good_evening, route_name='good-evening')
    return config.make_wsgi_app()
