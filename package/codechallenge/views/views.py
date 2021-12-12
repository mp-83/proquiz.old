import logging

from codechallenge.models import Question, User
from codechallenge.security import login_required
from pyramid.csrf import new_csrf_token
from pyramid.httpexceptions import HTTPBadRequest, HTTPSeeOther
from pyramid.security import forget, remember
from pyramid.view import view_config, view_defaults

logger = logging.getLogger(__name__)


@view_defaults(request_method="GET")
class CodeChallengeViews:
    def __init__(self, request):
        self.request = request

    @view_config(
        route_name="login",
        renderer="codechallenge:templates/login.jinja2",
        request_method="GET",
    )
    @view_config(
        route_name="login",
        renderer="codechallenge:templates/login.jinja2",
        request_method="POST",
    )
    def login(self):
        next_url = self.request.params.get("next", "")
        if not next_url:
            next_url = self.request.route_url("new_question")
        message = ""
        login = ""
        if self.request.method == "POST":
            email = self.request.params.get("email")
            password = self.request.params.get("password")
            user = self.request.dbsession.query(User).filter_by(email=email).first()
            if user is not None and user.check_password(password):
                new_csrf_token(self.request)
                headers = remember(self.request, user.uid)
                return HTTPSeeOther(location=next_url, headers=headers)
            raise HTTPBadRequest("Login failed")

        return {
            "message": message,
            "url": self.request.route_url("login"),
            "next_url": next_url,
            "login": login,
        }

    @view_config(route_name="logout", request_method="GET")
    @view_config(route_name="logout", request_method="POST")
    def logout(self):
        next_url = self.request.route_url("start")
        if self.request.method == "POST":
            new_csrf_token(self.request)
            headers = forget(self.request)
            return HTTPSeeOther(location=next_url, headers=headers)

        return HTTPSeeOther(location=next_url)

    @view_config(
        route_name="start", renderer="codechallenge:templates/start_page.jinja2"
    )
    def start(self):
        return {}

    @view_config(
        route_name="question", renderer="codechallenge:templates/question_page.jinja2"
    )
    def question(self):
        index = self.request.params.get("index", 0)
        result = Question().at_position(int(index))
        return result.json if result else {}

    @login_required
    @view_config(
        route_name="new_question",
        renderer="codechallenge:templates/new_question.jinja2",
        request_method="POST",
    )
    def new_question(self):
        data = getattr(self.request, "json", None)
        if not data:
            return {}
        new_question = Question(**data).save()
        # TODO - future
        # return Response(json=new_question.json)
        return new_question.json

    @login_required
    @view_config(
        route_name="edit_question",
        renderer="codechallenge:templates/new_question.jinja2",
        request_method="POST",
    )
    def edit_question(self):
        data = getattr(self.request, "json", None)
        if not data:
            return {}
        return {}

    @login_required
    @view_config(
        route_name="match",
        renderer="codechallenge:templates/new_question.jinja2",  # TODO: to fix
        request_method="POST",
    )
    def create_match(self):
        return {}
