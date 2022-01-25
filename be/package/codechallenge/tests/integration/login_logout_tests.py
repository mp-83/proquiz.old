import pytest
from codechallenge.endpoints.ep_match import CodeChallengeViews
from codechallenge.endpoints.ep_play import PlayViews
from codechallenge.entities import User
from pyramid.httpexceptions import HTTPBadRequest, HTTPSeeOther


class TestCaseLoginRequired:
    def t_checkDefaultEndPointsAreDecorated(self, dummy_request, config):
        protected_endpoints = (
            "new_question",
            "edit_question",
            "create_match",
        )
        endpoint_obj = CodeChallengeViews(dummy_request)
        for endpoint_name in protected_endpoints:
            endpoint_method = getattr(endpoint_obj, endpoint_name)
            response = endpoint_method()
            assert isinstance(response, HTTPSeeOther)

    def t_checkPlayViewsAreDecorated(self, dummy_request, config):
        protected_endpoints = ("start",)
        endpoint_obj = PlayViews(dummy_request)
        for endpoint_name in protected_endpoints:
            endpoint_method = getattr(endpoint_obj, endpoint_name)
            response = endpoint_method()
            assert isinstance(response, HTTPSeeOther)


class TestCaseLogin:
    def t_retrieveLoginPage(self, dummy_request, config):
        next_url = "new_question"
        view_obj = CodeChallengeViews(dummy_request)
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
        view_obj = CodeChallengeViews(request)
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
        view_obj = CodeChallengeViews(request)
        response = view_obj.login()
        assert isinstance(response, HTTPSeeOther)


class TestCaseLogOut:
    def t_successfulLogout(self, dummy_request, config):
        request = dummy_request
        request.method = "POST"
        view_obj = CodeChallengeViews(request)
        response = view_obj.logout()
        assert isinstance(response, HTTPSeeOther)
