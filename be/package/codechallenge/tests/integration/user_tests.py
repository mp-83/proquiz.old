from codechallenge.entities import Game, Match, Question, Reaction, User


class TestCaseUser:
    def t_list_all_players(self, testapp):
        match = Match().save()
        game = Game(match_uid=match.uid, index=0).save()
        user = User(email="user@test.project").save()
        question = Question(text="3*3 = ", time=0, position=0).save()
        Reaction(match=match, question=question, user=user, game_uid=game.uid).save()

        response = testapp.get("/players", status=200)
        assert response.json["players"]
