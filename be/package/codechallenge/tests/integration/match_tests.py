from codechallenge.endpoints.ep_match import CodeChallengeViews
from codechallenge.entities import Match
from codechallenge.tests.fixtures import TEST_1


class TestCaseMatchCreation:
    def t_successfulCreationOfAMatch(self, auth_request, config):
        request = auth_request
        request.method = "POST"
        view_obj = CodeChallengeViews(request)

        match_name = "New Sunday Match"
        request.json = {"name": match_name, "questions": TEST_1}
        view_obj = CodeChallengeViews(request)
        response = view_obj.create_match()
        match = Match().with_name(match_name)
        assert len(match.questions) == 4
        questions = response.json["match"]["questions"]
        assert questions[0]["text"] == TEST_1[0]["text"]
