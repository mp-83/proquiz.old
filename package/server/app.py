from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response
from pyramid.view import view_config


@view_config(route_name='hello', request_method='GET')
def hello_world(request):
    return Response('<body><h1>Hello World!!!</h1></body>')


def get_app(**settings):
    with Configurator() as config:
        config.add_route('hello', '/')
        config.add_view(hello_world, route_name='hello')
        config.scan()
        return config.make_wsgi_app()

def main():
    app = get_app()
    server = make_server('0.0.0.0', 5500, app)
    server.serve_forever()


if __name__ == '__main__':
    main()
    
