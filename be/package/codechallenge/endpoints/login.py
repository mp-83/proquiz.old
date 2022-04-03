import logging

from cerberus import Validator
from codechallenge.entities import User
from codechallenge.utils import view_decorator
from codechallenge.validation.syntax import user_login_schema
from pyramid.csrf import new_csrf_token
from pyramid.httpexceptions import HTTPSeeOther
from pyramid.response import Response
from pyramid.security import forget, remember

logger = logging.getLogger(__name__)


class Login:
    def __init__(self, request):
        self.request = request

    @view_decorator(
        route_name="home", request_method="GET", renderer="templates/home_page.jinja2"
    )
    def home(self):
        return {}

    @view_decorator(route_name="login", request_method="POST", require_csrf=False)
    def login(self):
        user_data = getattr(self.request, "json", None)
        v = Validator(user_login_schema)
        if not v.validate(user_data):
            return Response(status=400, json=v.errors)

        # TODO to fix later
        next_url = self.request.params.get("next", "")
        if not next_url:
            next_url = self.request.route_url("list_matches")

        email = v.document.get("email")
        password = v.document.get("password")
        user = self.request.dbsession.query(User).filter_by(email=email).first()
        if user is not None and user.check_password(password):
            new_csrf_token(self.request)
            headers = remember(self.request, user.uid)
            print(f"Headers ==> {headers}")
            return HTTPSeeOther(location=next_url, headers=headers)
        return Response(status=400, json={"error": "Login failed"})


class Logout:
    def __init__(self, request):
        self.request = request

    @view_decorator(route_name="logout", request_method="GET")
    @view_decorator(route_name="logout", request_method="POST")
    def logout(self):
        next_url = self.request.route_url("home")
        if self.request.method == "POST":
            new_csrf_token(self.request)
            headers = forget(self.request)
            return HTTPSeeOther(location=next_url, headers=headers)

        return HTTPSeeOther(location=next_url)
