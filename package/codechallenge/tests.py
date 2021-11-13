import pytest
from pyramid import testing


class TestCaseTutorialView:
    def test_start_view(self):
        from codechallenge.views import CodeChallengeViews

        request = testing.DummyRequest()
        view_obj = CodeChallengeViews(request)
        response = view_obj.start()
        assert response['name'] == 'Marco'

    def test_question_view(self):
        from codechallenge.views import CodeChallengeViews

        request = testing.DummyRequest()
        view_obj = CodeChallengeViews(request)
        response = view_obj.question()
        assert response == {'code': '', 'text': ''}


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
        res = self.testapp.get('/question', status=200)
        assert b'Start' in res.body
