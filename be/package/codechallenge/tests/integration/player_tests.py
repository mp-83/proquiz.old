from codechallenge.endpoints.play import PlayEndPoints
from codechallenge.tests.fixtures import TEST_1


class TestCasePlay:
    def t_startGame(self, auth_request, config, trivia_match):
        request = auth_request
        request.method = "POST"
        request.json = {"name": trivia_match.name}
        view_obj = PlayEndPoints(request)

        response = view_obj.start()
        assert response.json["question"] == TEST_1[0]["text"]
        assert len(response.json["answers"]) == 4
