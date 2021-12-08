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

    def t_defaultMessageIsRenderedIfNoQuestionsArePresent(self):
        res = self.testapp.get("/question", status=200, params={"index": 1})
        assert b"No Questions" in res.body

    def t_postRequestWithoutCSRFTokenReturns400(self):
        self.testapp.post_json("/new_question", status=400)

    def t_newQuestionPageRequiresLogin(self):
        # CSRF token is needed also in this case
        res = self.testapp.post_json(
            "/new_question",
            status=303,
            headers={"X-CSRF-Token": self.testapp.get_csrf_token()},
        )
        assert b"/login" in res.body

    def t_malformedLoginPayload(self, functional_config):
        self.testapp.post(
            "/login",
            status=400,
            params={"email": "user"},
            headers={"X-CSRF-Token": self.testapp.get_csrf_token()},
        )

    def t_cookiesAfterLogoutCompletedSuccessfully(self, functional_config):
        response = self.testapp.post(
            "/logout",
            status=303,
            headers={"X-CSRF-Token": self.testapp.get_csrf_token()},
        )
        assert "Set-Cookie" in dict(response.headers)

    def t_usingGetInsteadOfPostWhenCallingLogout(self, functional_config):
        response = self.testapp.get("/logout", status=303)
        assert "Set-Cookie" not in dict(response.headers)

    def t_usingNotAllowedMethodsResultsIn404not405(self):
        self.testapp.post("/question", status=404)
        self.testapp.patch("/", status=404)
