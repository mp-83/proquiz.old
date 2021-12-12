import pytest
from codechallenge.db import count
from codechallenge.models import Question, User
from codechallenge.views.views import CodeChallengeViews
from pyramid import testing
from pyramid.httpexceptions import HTTPBadRequest, HTTPSeeOther


class TestCaseTutorialView:
    def t_start_view(self):
        request = testing.DummyRequest()
        view_obj = CodeChallengeViews(request)
        response = view_obj.start()
        assert response == {}

    def t_textCodeAndPositionAreReturnedWhenQuestionIsFound(self, fillTestingDB):
        request = testing.DummyRequest()
        request.params.update(index=2)
        view_obj = CodeChallengeViews(request)
        response = view_obj.question()
        assert response == {"text": "q2.text", "code": "q2.code", "position": 2}

    def t_whenQuestionIsNoneEmptyDictIsReturned(self, fillTestingDB):
        request = testing.DummyRequest()
        request.params.update(index=30)
        view_obj = CodeChallengeViews(request)
        response = view_obj.question()
        assert response == {}

    def t_createNewQuestion(self, dummy_request, mocker):
        mocker.patch("pyramid.testing.DummyRequest.is_authenticated")
        request = dummy_request
        request.json = {
            "text": "eleven pm",
            "code": "x = 0; x += 1; print(x)",
            "position": 2,
        }
        view_obj = CodeChallengeViews(request)
        response = view_obj.new_question()
        assert count(Question) == 1
        assert response["text"] == "eleven pm"
        assert response["position"] == 2


class TestCaseLoginRequired:
    def t_checkViewsAreDecorated(self, dummy_request, simple_config):
        protected_views = (
            "new_question",
            "edit_question",
            "create_match",
            # "edit_match",
        )
        view_obj = CodeChallengeViews(dummy_request)
        for view_name in protected_views:
            view_method = getattr(view_obj, view_name)
            response = view_method()
            assert isinstance(response, HTTPSeeOther)


class TestCaseLogin:
    def t_retrieveLoginPage(self, dummy_request, simple_config):
        next_url = "new_question"
        view_obj = CodeChallengeViews(dummy_request)
        response = view_obj.login()
        assert response["next_url"].endswith(next_url)
        assert response["url"].endswith("login")

    def t_failedLoginAttempt(self, dummy_request, simple_config):
        request = dummy_request
        request.method = "POST"
        request.params = {
            "email": "user@test.com",
            "password": "p@ss",
        }
        view_obj = CodeChallengeViews(request)
        with pytest.raises(HTTPBadRequest):
            view_obj.login()

    def t_successfulLogin(self, dummy_request, simple_config):
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
    def t_successfulLogout(self, dummy_request, simple_config):
        request = dummy_request
        request.method = "POST"
        view_obj = CodeChallengeViews(request)
        response = view_obj.logout()
        assert isinstance(response, HTTPSeeOther)


class TestCaseMatch:
    def t_successfulCreationOfAMatch(self, dummy_request, simple_config):
        request = dummy_request
        request.method = "POST"
        view_obj = CodeChallengeViews(request)

        match_name = "New Sunday Match"
        request.params = {"name": match_name, "questions": [{"text": "what time "}]}
        view_obj = CodeChallengeViews(request)
        response = view_obj.create_match()
        assert response["name"] == match_name
