from codechallenge.endpoints.match import MatchEndPoints
from codechallenge.endpoints.play import PlayEndPoints
from codechallenge.endpoints.question import QuestionEndPoints
from codechallenge.entities import User
from pyramid.httpexceptions import HTTPSeeOther


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
    def t_failedLoginAttempt(self, testapp):
        credentials = {
            "email": "user@test.com",
            "password": "psser",
        }
        testapp.post(
            "/login",
            status=400,
            params=credentials,
            headers={"X-CSRF-Token": testapp.get_csrf_token()},
        )

    def t_successfulLogin(self, testapp):
        credentials = {
            "email": "user@test.com",
            "password": "p@ss",
        }
        User(**credentials).create()
        testapp.post(
            "/login",
            status=303,
            params=credentials,
            headers={"X-CSRF-Token": testapp.get_csrf_token()},
        )

    def t_malformedLoginPayload(self, testapp):
        testapp.post(
            "/login",
            status=400,
            params={"email": "user"},
            headers={"X-CSRF-Token": testapp.get_csrf_token()},
        )


class TestCaseLogOut:
    def t_cookiesAfterLogoutCompletedSuccessfully(self, testapp):
        response = testapp.post(
            "/logout",
            status=303,
            headers={"X-CSRF-Token": testapp.get_csrf_token()},
        )
        assert "Set-Cookie" in dict(response.headers)

    def t_usingGetInsteadOfPostWhenCallingLogout(self, testapp):
        response = testapp.get("/logout", status=303)
        assert "Set-Cookie" not in dict(response.headers)
