import pytest


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

    def t_wrongMethodsReturn404not405(self, sessionTestDB):
        self.testapp.post("/question", status=404)
        self.testapp.patch("/", status=404)
