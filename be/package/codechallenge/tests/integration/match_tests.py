from codechallenge.entities import Game, Match, Question, Questions
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
        match_name = "New Match"
        match = Match(name=match_name).create()
        first_game = Game(match_uid=match.uid, index=1).create()
        Question(text="Where is London?", game_uid=first_game.uid).save()
        second_game = Game(match_uid=match.uid, index=2).create()
        Question(text="Where is Vienna?", game_uid=second_game.uid).save()

        response = testapp.get(f"/match/{match.uid}", status=200)
        assert response.json == {
            "match": {
                "name": match_name,
                "questions": [
                    {"code": None, "position": 0, "text": "Where is London?"},
                    {"code": None, "position": 1, "text": "Where is Vienna?"},
                ],
            }
        }
