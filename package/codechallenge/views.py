from pyramid.response import Response
from pyramid.view import view_config


class CodeChallengeViews:
    
    def __init__(self, request):
        self.request = request

    @view_config(route_name='start', renderer='start_page.jinja2')
    def start(self):
        return {'name': 'Marco'}

    @view_config(route_name='question', renderer='question_page.jinja2')
    def question(self):
        return {
            'text': '',
            'code': ''
        }
