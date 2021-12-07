import logging

from codechallenge.models.question import Question
from pyramid.view import view_config, view_defaults

logger = logging.getLogger(__name__)


@view_defaults(request_method="GET")
class CodeChallengeViews:
    def __init__(self, request):
        self.request = request

    @view_config(
        route_name="start", renderer="codechallenge:templates/start_page.jinja2"
    )
    def start(self):
        logger.info("Start page")
        return {}

    @view_config(
        route_name="question", renderer="codechallenge:templates/question_page.jinja2"
    )
    def question(self):
        index = self.request.params.get("index", 0)
        result = Question().at_position(int(index))
        return result.json if result else {}

    @view_config(
        route_name="new_question",
        renderer="codechallenge:templates/new_question.jinja2",
        request_method="POST",
    )
    def new_question(self):
        data = self.request.json
        if not data:
            return {}
        new_question = Question(**data).save()
        # TODO - future
        # return Response(json=new_question.json)
        return new_question.json

    @view_config(route_name="login", renderer="codechallenge:templates/login.jinja2")
    def login(self):
        next_url = self.request.params.get("next", "")
        if not next_url:
            next_url = self.request.route_url("new_question")
        message = ""
        login = ""
        # if self.request.method == 'POST':
        #     login = self.request.params['login']
        #     password = self.request.params['password']
        #     user = (
        #         self.request.dbsession.query(models.User)
        #         .filter_by(name=login)
        #         .first()
        #     )
        #     if user is not None and user.check_password(password):
        #         new_csrf_token(request)
        #         headers = remember(request, user.id)
        #         return HTTPSeeOther(location=next_url, headers=headers)
        #     message = 'Failed login'
        #     self.request.response.status = 400

        return {
            "message": message,
            "url": self.request.route_url("login"),
            "next_url": next_url,
            "login": login,
        }
