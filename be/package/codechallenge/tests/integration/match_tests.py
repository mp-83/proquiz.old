from codechallenge.entities import Game, Match, Question, Questions, Reaction, User
from codechallenge.tests.fixtures import TEST_1


class TestCaseMatchEndpoints:
    def t_successfulCreationOfAMatch(self, testapp):
        match_name = "New Match"
        response = testapp.post_json(
            "/match/new",
            {"name": match_name, "questions": TEST_1},
            headers={"X-CSRF-Token": testapp.get_csrf_token()},
            status=200,
        )

        assert Questions.count() == 4
        questions = response.json["match"]["questions"]
        assert questions[0][0]["text"] == TEST_1[0]["text"]

    def t_requestUnexistentMatch(self, testapp):
        testapp.get("/match/30", status=404)

    def t_retriveOneMatchWithAllData(self, testapp):
        match_name = "New Match"
        match = Match(name=match_name).create()
        first_game = Game(match_uid=match.uid).create()
        Question(text="Where is London?", game_uid=first_game.uid, position=0).save()
        second_game = Game(match_uid=match.uid, index=1).create()
        Question(text="Where is Vienna?", game_uid=second_game.uid, position=0).save()

        response = testapp.get(f"/match/{match.uid}", status=200)
        assert response.json == {
            "match": {
                "name": match_name,
                "is_restricted": True,
                "expires": None,
                "order": True,
                "times": 1,
                "questions": [
                    [
                        {
                            "code": None,
                            "position": 0,
                            "text": "Where is London?",
                            "answers": [],
                        }
                    ],
                    [
                        {
                            "code": None,
                            "position": 0,
                            "text": "Where is Vienna?",
                            "answers": [],
                        }
                    ],
                ],
            }
        }

    def t_matchCannotBeChangedIfStarted(self, testapp):
        match_name = "New Match"
        match = Match(name=match_name).create()
        first_game = Game(match_uid=match.uid).create()
        question = Question(
            text="Where is London?", game_uid=first_game.uid, position=0
        ).save()
        user = User(email="t@t.com").create()
        Reaction(match=match, question=question, user=user).create()
        testapp.patch_json(
            f"/match/edit/{match.uid}",
            headers={"X-CSRF-Token": testapp.get_csrf_token()},
            status=400,
        )

    def t_addQuestionToExistingMatchWithOneGameOnly(self, testapp):
        match = Match().create()
        first_game = Game(match_uid=match.uid).create()
        Question(text="Where is London?", game_uid=first_game.uid, position=0).save()
        payload = {
            "questions": [
                {
                    "game": first_game.index,
                    "text": "What is the capital of Sweden?",
                    "answers": [
                        {"text": "Stockolm"},
                        {"text": "Oslo"},
                        {"text": "London"},
                    ],
                }
            ],
        }
        testapp.patch_json(
            f"/match/edit/{match.uid}",
            payload,
            headers={"X-CSRF-Token": testapp.get_csrf_token()},
            status=200,
        )

        match.refresh()
        assert len(match.questions[0]) == 2
        assert len(first_game.ordered_questions) == 2

    def t_changeNameAndTimesOfAMatch(self, testapp):
        # showcase that changing the attribute value of a match work
        match = Match(name="New Match").create()
        payload = {
            "name": "Another match name",
            "times": 10,
        }
        testapp.patch_json(
            f"/match/edit/{match.uid}",
            payload,
            headers={"X-CSRF-Token": testapp.get_csrf_token()},
            status=200,
        )

        match.refresh()
        assert match.name == "Another match name"
        assert match.times == 10
