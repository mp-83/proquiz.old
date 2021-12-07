import pytest


class TestCaseCodeChallengeFunctional:
    @pytest.fixture(autouse=True)
    def setUp(self, testapp):
        self.testapp = testapp

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

    def t_createNewQuestion(self, sessionTestDB, testapp):
        payload = {"text": "new question", "code": "let var x = 0"}
        res = self.testapp.post_json(
            "/new_question",
            status=302,
            params=payload,
            headers={"X-CSRF-Token": testapp.get_csrf_token()},
        )
        assert b"/login" in res.body
        # assert b"Answers" in res.body

    def t_wrongMethodsReturn404not405(self, sessionTestDB):
        self.testapp.post("/question", status=404)
        self.testapp.patch("/", status=404)
