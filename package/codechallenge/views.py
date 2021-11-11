from pyramid.response import Response
from pyramid.view import view_config


class CodeChallengeViews:
    
    def __init__(self, request):
        self.request = request    

    @view_config(route_name='home', renderer='home_page.jinja2')
    def home(self):
        test_route = '/test'
        return {'name': 'Marco'}


    @view_config(route_name='test', renderer='question_page.jinja2')
    def interview_test(self):
        return {}
