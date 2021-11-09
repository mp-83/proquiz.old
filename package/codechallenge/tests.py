import pytest
from pyramid import testing


class TestCaseTutorialView:
    def test_home_view(self):
        from codechallenge.views import CodeChallengeViews

        request = testing.DummyRequest()
        view_obj = CodeChallengeViews(request)
        response = view_obj.home()
        assert response['name'] == 'Marco'


class TestCaseTutorialFunctional:
    @pytest.fixture(autouse=True)
    def setUp(self):
        from codechallenge import main
        app = main({})
        from webtest import TestApp

        self.testapp = TestApp(app)

    def test_home_page(self):
        res = self.testapp.get('/', status=200)
        assert b'Welcome' in res.body

    def test_test_page(self):
        res = self.testapp.get('/test', status=200)
        assert b'Start' in res.body
