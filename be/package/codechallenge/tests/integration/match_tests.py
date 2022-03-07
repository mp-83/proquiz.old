from codechallenge.entities import Game, Match, Question, Questions, Reaction, User
from codechallenge.tests.fixtures import TEST_1


class TestCaseBadRequest:
    # verify that syntax check occurs before
    # logical one
    def t_creation(self, testapp):
        testapp.post_json(
            "/match/new",
            {"questions": None},
            headers={"X-CSRF-Token": testapp.get_csrf_token()},
            status=400,
        )

    def t_update(self, testapp):
        testapp.patch_json(
            "/match/edit/1",
            {"questions": None},
            headers={"X-CSRF-Token": testapp.get_csrf_token()},
            status=400,
        )


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
        match = Match(name=match_name).save()
        first_game = Game(match_uid=match.uid).save()
        Question(text="Where is London?", game_uid=first_game.uid, position=0).save()
        second_game = Game(match_uid=match.uid, index=1).save()
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
        match = Match(name=match_name).save()
        first_game = Game(match_uid=match.uid).save()
        question = Question(
            text="Where is London?", game_uid=first_game.uid, position=0
        ).save()
        user = User(email="t@t.com").save()
        Reaction(match=match, question=question, user=user).save()
        response = testapp.patch_json(
            f"/match/edit/{match.uid}",
            {"times": 1},
            headers={"X-CSRF-Token": testapp.get_csrf_token()},
            status=400,
        )
        assert response.json["error"] == "Match started. Cannot be edited"

    def t_addQuestionToExistingMatchWithOneGameOnly(self, testapp):
        match = Match().save()
        first_game = Game(match_uid=match.uid).save()
        Question(text="Where is London?", game_uid=first_game.uid, position=0).save()
        payload = {
            "times": 10,
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
        assert match.times == 10

    def t_listAllMatches(self, testapp):
        m1 = Match().save()
        m2 = Match().save()
        m3 = Match().save()

        response = testapp.get(
            "/match/list",
            status=200,
        )

        rjson = response.json
        assert rjson["matches"] == [m.json for m in [m1, m2, m3]]
