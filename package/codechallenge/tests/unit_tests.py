import pytest
from codechallenge.app import StoreConfig
from codechallenge.db import count
from codechallenge.models.answer import Answer
from codechallenge.models.question import Question
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


class TestCaseQuestion:
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


class TestCaseCodeChallengeFunctional:
    @pytest.fixture(autouse=True)
    def setUp(self, settings):
        from codechallenge import main

        app = main({}, **settings)

        from webtest import TestApp

        self.testapp = TestApp(app)

    def t_start_page(self):
        res = self.testapp.get("/", status=200)
        assert b"Welcome" in res.body

    def t_relativeSectionIsRenderedWhenQuestionIsFound(self, fillTestingDB):
        res = self.testapp.get("/question", status=200, params={"index": 1})
        assert b"Q.1" in res.body
        assert b"q1.text" in res.body

    def t_defaultMessageIsRenderedIfNoQuestionsArePresent(self, sessionTestDB):
        res = self.testapp.get("/question", status=200, params={"index": 1})
        assert b"No Questions" in res.body

    def t_question_page_wrong_method(self):
        self.testapp.post("/question", status=404)

    def t_start_page_wrong_method(self):
        self.testapp.patch("/", status=404)
