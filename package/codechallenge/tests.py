import pytest
from pyramid import testing
from sqlalchemy.exc import IntegrityError, InvalidRequestError

from codechallenge.models.question import Question
from codechallenge.models.answer import Answer
from codechallenge.views import CodeChallengeViews
from codechallenge.app import StoreConfig
from codechallenge.db import count


class TestCaseConfigSingleton:
    def test_that_works_as_expected(self):
        sc = StoreConfig()
        settings_mock = {'setting': True}
        sc.config = settings_mock
        for _ in range(2):
            assert sc is StoreConfig()
            assert sc.config is settings_mock


class TestCaseQuestion:
    def test_all_questions(self, initTestingDB):
        assert len(Question().all()) == 3

    def test_question_at_position(self, initTestingDB):
        question = Question().at_position(1)
        assert question.text == 'q1.text'
        
    def test_appending_questions_to_answer(self, initTestingDB):
        question = Question().at_position(1)
        assert question.uid
        a1 = Answer(question=question, text='question2.answer1', pos=1).create()
        a2 = Answer(question=question, text='question2.answer2', pos=2).create()
        assert a1.uid
        assert count(Answer) == 2
        assert question.answers[0].question_uid == question.uid

    def test_all_answer_of_same_question_must_differ(self, initTestingDB):
        question = Question().at_position(2)
        with pytest.raises((IntegrityError, InvalidRequestError)):
            question.answers.extend([
                Answer(text='question2.answer1', pos=1),
                Answer(text='question2.answer1', pos=2)
            ])
            question.save()
            
        current_session = StoreConfig().session
        current_session.rollback


class TestCaseTutorialView:
    def test_start_view(self):
        request = testing.DummyRequest()
        view_obj = CodeChallengeViews(request)
        response = view_obj.start()
        assert response == {}

    def test_question_view(self, mocker):
        question_sample = {
            'text': 'This is an expression or a statement?',
            'code': 'x += 1', 
        }
        patched_method = mocker.patch(
            'codechallenge.views.read_question', return_value=question_sample
        )
        request = testing.DummyRequest()
        request.params.update(index=2)
        view_obj = CodeChallengeViews(request)
        response = view_obj.question()
        
        expected = question_sample.copy()
        expected.update(index=2)
        assert response == expected


class TestCaseCodeChallengeFunctional:
    @pytest.fixture(autouse=True)
    def setUp(self):
        from codechallenge import main
        app = main({})
        from webtest import TestApp

        self.testapp = TestApp(app)

    def test_start_page(self):
        res = self.testapp.get('/', status=200)
        assert b'Welcome' in res.body

    def test_question_page(self):
        res = self.testapp.get('/question', status=200, params={'index': 1})
        assert b'Q.1' in res.body

    def test_question_page_wrong_method(self):
        self.testapp.post('/question', status=404)

    def test_start_page_wrong_method(self):
        self.testapp.patch('/', status=404)
