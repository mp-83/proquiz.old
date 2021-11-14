from pyramid.response import Response
from pyramid.view import view_config, view_defaults
from codechallenge.db import read_question


@view_defaults(request_method='GET')
class CodeChallengeViews:
    
    def __init__(self, request):
        self.request = request

    @view_config(route_name='start', renderer='start_page.jinja2')
    def start(self):
        return {}

    @view_config(route_name='question', renderer='question_page.jinja2')
    def question(self):
        index = self.request.params.get('index', 0)
        result = read_question(int(index))
        result.update(index=index)
        return result
