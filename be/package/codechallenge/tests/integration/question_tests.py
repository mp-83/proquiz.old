from codechallenge.endpoints.ep_match import CodeChallengeViews
from codechallenge.entities import Questions


class TestCaseQuestionEP:
    def t_start_view(self, dummy_request):
        view_obj = CodeChallengeViews(dummy_request)
        response = view_obj.home()
        assert response == {}

    def t_textCodeAndPositionAreReturnedWhenQuestionIsFound(
        self, fillTestingDB, dummy_request
    ):
        request = dummy_request
        request.params.update(index=2)
        view_obj = CodeChallengeViews(request)
        response = view_obj.question()
        assert response == {"text": "q2.text", "code": "q2.code", "position": 2}

    def t_whenQuestionIsNoneEmptyDictIsReturned(self, fillTestingDB, dummy_request):
        request = dummy_request
        request.params.update(index=30)
        view_obj = CodeChallengeViews(request)
        response = view_obj.question()
        assert response == {}

    def t_createNewQuestion(self, dummy_request, mocker):
        mocker.patch("pyramid.testing.DummyRequest.is_authenticated")
        request = dummy_request
        request.json = {
            "text": "eleven pm",
            "code": "x = 0; x += 1; print(x)",
            "position": 2,
        }
        view_obj = CodeChallengeViews(request)
        response = view_obj.new_question()
        assert Questions.count() == 1
        assert response.json["text"] == "eleven pm"
        assert response.json["position"] == 2
