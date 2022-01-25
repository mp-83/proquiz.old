import logging

from codechallenge.entities import User
from pyramid.csrf import new_csrf_token
from pyramid.httpexceptions import HTTPBadRequest, HTTPSeeOther
from pyramid.security import forget, remember
from pyramid.view import view_config, view_defaults

logger = logging.getLogger(__name__)


@view_defaults(request_method="GET")
class Login:
    def __init__(self, request):
        self.request = request

    @view_config(route_name="home", renderer="codechallenge:templates/home_page.jinja2")
    def home(self):
        return {}

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


@view_defaults(request_method="GET")
class Logout:
    def __init__(self, request):
        self.request = request

    @view_config(route_name="logout", request_method="GET")
    @view_config(route_name="logout", request_method="POST")
    def logout(self):
        next_url = self.request.route_url("home")
        if self.request.method == "POST":
            new_csrf_token(self.request)
            headers = forget(self.request)
            return HTTPSeeOther(location=next_url, headers=headers)

        return HTTPSeeOther(location=next_url)
