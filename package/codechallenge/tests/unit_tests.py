import pytest
from codechallenge.app import StoreConfig
from codechallenge.db import count
from codechallenge.models import Answer, Question, User
from codechallenge.views.views import CodeChallengeViews
from pyramid import testing
from pyramid.httpexceptions import HTTPBadRequest, HTTPFound, HTTPSeeOther
from sqlalchemy.exc import IntegrityError, InvalidRequestError


class TestCaseConfigSingleton:
    def t_singletonHasToBeCreatedOnce(self):
        sc = StoreConfig()
        settings_mock = {"setting": True}
        sc.config = settings_mock
        for _ in range(2):
            assert sc is StoreConfig()
            assert sc.config is settings_mock


class TestCaseModels:
    def t_countMethodReturnsTheCorrectValue(self, fillTestingDB):
        assert count(Question) == 3

    def t_theQuestionAtPositionShouldBeReturned(self, fillTestingDB):
        question = Question().at_position(1)
        assert question.text == "q1.text"

    def t_newCreatedAnswersShouldBeAvailableFromTheQuestion(self, fillTestingDB):
        question = Question().at_position(1)
        Answer(question=question, text="question2.answer1", position=1).create()
        Answer(question=question, text="question2.answer2", position=2).create()
        assert count(Answer) == 2
        assert question.answers[0].question_uid == question.uid

    def t_editingTextOfExistingQuestion(self, fillTestingDB):
        question = Question().at_position(2)
        question.update(text="new-text")
        assert question.text == "new-text"

    def t_createQuestionWithoutPosition(self, fillTestingDB):
        new_question = Question(text="new-question").save()
        assert new_question.position == 4

    def t_allAnswersOfAQuestionMustDiffer(self, fillTestingDB):
        question = Question().at_position(2)
        with pytest.raises((IntegrityError, InvalidRequestError)):
            question.answers.extend(
                [
                    Answer(text="question2.answer1", position=1),
                    Answer(text="question2.answer1", position=2),
                ]
            )
            question.save()

        current_session = StoreConfig().session
        current_session.rollback

    def t_createNewUserAndSetPassword(self, sessionTestDB):
        new_user = User(email="user@test.project").create()
        new_user.set_password("password")
        new_user.save()
        assert new_user.check_password("password")


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
    def t_checkViewsAreDecorated(self, dummy_request, dummy_config):
        view_obj = CodeChallengeViews(dummy_request)
        for view_name in ["new_question", "edit_question"]:
            view_method = getattr(view_obj, view_name)
            response = view_method()
            assert isinstance(response, HTTPFound)


class TestCaseLogin:
    def t_retrieveLoginPage(self, dummy_request, dummy_config):
        next_url = "new_question"
        view_obj = CodeChallengeViews(dummy_request)
        response = view_obj.login()
        assert response["next_url"].endswith(next_url)
        assert response["url"].endswith("login")

    def t_failedLoginAttempt(self, dummy_request, dummy_config):
        request = dummy_request
        request.method = "POST"
        request.params = {
            "email": "user@test.com",
            "password": "p@ss",
        }
        view_obj = CodeChallengeViews(request)
        with pytest.raises(HTTPBadRequest):
            view_obj.login()

    def t_successfulLogin(self, dummy_request, dummy_config):
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
