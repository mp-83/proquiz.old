from codechallenge.endpoints.question import QuestionEndPoints
from codechallenge.entities import Questions


class TestCaseQuestionEP:
    def t_textCodeAndPositionAreReturnedWhenQuestionIsFound(
        self, fillTestingDB, dummy_request
    ):
        request = dummy_request
        request.params.update(index=2)
        view_obj = QuestionEndPoints(request)
        response = view_obj.question()
        assert response == {"text": "q2.text", "code": "q2.code", "position": 2}

    def t_whenQuestionIsNoneEmptyDictIsReturned(self, fillTestingDB, dummy_request):
        request = dummy_request
        request.params.update(index=30)
        view_obj = QuestionEndPoints(request)
        response = view_obj.question()
        assert response == {}

    def t_createNewQuestion(self, testapp):
        # CSRF token is needed also in this case
        response = testapp.post_json(
            "/new_question",
            {
                "text": "eleven pm",
                "code": "x = 0; x += 1; print(x)",
                "position": 2,
            },
            status=200,
            headers={"X-CSRF-Token": testapp.get_csrf_token()},
        )
        assert Questions.count() == 1
        assert response.json["text"] == "eleven pm"
        assert response.json["position"] == 2
