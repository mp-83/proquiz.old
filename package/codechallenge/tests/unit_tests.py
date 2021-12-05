import pytest
from codechallenge.app import StoreConfig
from codechallenge.db import count
from codechallenge.models import Answer, Question, User
from codechallenge.views import CodeChallengeViews
from pyramid import testing
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
        new_user = User(name="marco").create()
        new_user.set_password("password")
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

    def t_insert_view(self, sessionTestDB):
        request = testing.DummyRequest()
        request.params.update(
            data={
                "text": "eleven pm",
                "code": "x = 0; x += 1; print(x)",
                "position": 1,
            }
        )
        view_obj = CodeChallengeViews(request)
        response = view_obj.insert_question()
        assert count(Question) == 1
        assert response["text"] == "eleven pm"
