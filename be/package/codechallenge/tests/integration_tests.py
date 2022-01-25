import pytest
from codechallenge.endpoints.ep_match import CodeChallengeViews
from codechallenge.endpoints.ep_play import PlayViews
from codechallenge.entities import Match, Question, Questions, User
from codechallenge.tests.fixtures import TEST_1
from pyramid.httpexceptions import HTTPBadRequest, HTTPSeeOther


class TestCaseTutorialView:
    def t_start_view(self, dummy_request):
        view_obj = CodeChallengeViews(dummy_request)
        response = view_obj.home()
        assert response == {}

    def t_textCodeAndPositionAreReturnedWhenQuestionIsFound(
        self, fillTestingDB, dummy_request
    ):
        request = dummy_request
        request.params.update(index=2)
        view_obj = CodeChallengeViews(request)
        response = view_obj.question()
        assert response == {"text": "q2.text", "code": "q2.code", "position": 2}

    def t_whenQuestionIsNoneEmptyDictIsReturned(self, fillTestingDB, dummy_request):
        request = dummy_request
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
        assert Questions.count() == 1
        assert response.json["text"] == "eleven pm"
        assert response.json["position"] == 2


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


class TestCaseMatch:
    def t_successfulCreationOfAMatch(self, auth_request, config):
        request = auth_request
        request.method = "POST"
        view_obj = CodeChallengeViews(request)

        match_name = "New Sunday Match"
        request.json = {"name": match_name, "questions": TEST_1}
        view_obj = CodeChallengeViews(request)
        response = view_obj.create_match()
        match = Match().with_name(match_name)
        assert len(match.questions) == 4
        questions = response.json["match"]["questions"]
        assert questions[0]["text"] == TEST_1[0]["text"]


class TestCasePlayViews:
    def t_startGame(self, auth_request, config, trivia_match):
        request = auth_request
        request.method = "POST"
        request.json = {"name": trivia_match.name}
        view_obj = PlayViews(request)

        response = view_obj.start()
        assert response.json["question"] == TEST_1[0]["text"]
        assert len(response.json["answers"]) == 4
