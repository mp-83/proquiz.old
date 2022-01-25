import pytest
from codechallenge.endpoints.login import Login, Logout
from codechallenge.endpoints.match import MatchEndPoints
from codechallenge.endpoints.play import PlayEndPoints
from codechallenge.endpoints.question import QuestionEndPoints
from codechallenge.entities import User
from pyramid.httpexceptions import HTTPBadRequest, HTTPSeeOther


class TestCaseLoginRequired:
    def t_checkDefaultEndPointsAreDecorated(self, dummy_request, config):
        protected_endpoints = (
            (QuestionEndPoints, "new_question"),
            (QuestionEndPoints, "edit_question"),
            (MatchEndPoints, "create_match"),
        )
        for endpoint_cls, endpoint_name in protected_endpoints:
            endpoint_obj = endpoint_cls(dummy_request)
            endpoint_method = getattr(endpoint_obj, endpoint_name)
            response = endpoint_method()
            assert isinstance(response, HTTPSeeOther)

    def t_checkPlayViewsAreDecorated(self, dummy_request, config):
        protected_endpoints = ((PlayEndPoints, "start"),)
        for endpoint_cls, endpoint_name in protected_endpoints:
            endpoint_obj = endpoint_cls(dummy_request)
            endpoint_method = getattr(endpoint_obj, endpoint_name)
            response = endpoint_method()
            assert isinstance(response, HTTPSeeOther)


class TestCaseLogin:
    def t_start_view(self, dummy_request):
        view_obj = Login(dummy_request)
        response = view_obj.home()
        assert response == {}

    def t_retrieveLoginPage(self, dummy_request, config):
        next_url = "new_question"
        view_obj = Login(dummy_request)
        response = view_obj.login()
        assert response["next_url"].endswith(next_url)
        assert response["url"].endswith("login")

    def t_failedLoginAttempt(self, dummy_request, config):
        request = dummy_request
        request.method = "POST"
        request.params = {
            "email": "user@test.com",
            "password": "p@ss",
        }
        view_obj = Login(request)
        with pytest.raises(HTTPBadRequest):
            view_obj.login()

    def t_successfulLogin(self, dummy_request, config):
        credentials = {
            "email": "user@test.com",
            "password": "p@ss",
        }
        User(**credentials).create()
        request = dummy_request
        request.method = "POST"
        request.params = credentials
        view_obj = Login(request)
        response = view_obj.login()
        assert isinstance(response, HTTPSeeOther)


class TestCaseLogOut:
    def t_successfulLogout(self, dummy_request, config):
        request = dummy_request
        request.method = "POST"
        view_obj = Logout(request)
        response = view_obj.logout()
        assert isinstance(response, HTTPSeeOther)
