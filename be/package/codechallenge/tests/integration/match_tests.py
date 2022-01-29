from codechallenge.entities import Questions
from codechallenge.tests.fixtures import TEST_1


class TestCaseMatchCreation:
    def t_successfulCreationOfAMatch(self, testapp):
        match_name = "New Match"
        response = testapp.post_json(
            "/match",
            {"name": match_name, "questions": TEST_1},
            headers={"X-CSRF-Token": testapp.get_csrf_token()},
            status=200,
        )

        assert Questions.count() == 4
        questions = response.json["match"]["questions"]
        assert questions[0]["text"] == TEST_1[0]["text"]

    def t_retriveOneMatchWithAllData(self, testapp):
        response = testapp.get("/match", status=200)
        assert response.json == {"match": {}}
