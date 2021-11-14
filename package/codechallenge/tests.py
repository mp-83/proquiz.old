import pytest
from pyramid import testing
from codechallenge.views import CodeChallengeViews



class TestCaseTutorialView:
    def test_start_view(self):
        request = testing.DummyRequest()
        view_obj = CodeChallengeViews(request)
        response = view_obj.start()
        assert response['name'] == 'Marco'

    def test_question_view(self, mocker):
        question_sample = {
            'text': 'This is an expression or a statement?',
            'code': 'x += 1', 
        }
        patched_method = mocker.patch(
            'codechallenge.views.read_question', return_value=question_sample
        )
        request = testing.DummyRequest()
        view_obj = CodeChallengeViews(request)
        response = view_obj.question()
        question_sample.update(index=0)
        assert response == question_sample


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
