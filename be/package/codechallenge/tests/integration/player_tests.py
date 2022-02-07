from datetime import datetime, timedelta, timezone

from codechallenge.entities import Game, Match, Question, Reaction, User


class TestCasePlay:
    def t_playLand(self, testapp):
        match = Match().create()
        response = testapp.post_json(
            "/play/",
            {"match": match.uid},
            headers={"X-CSRF-Token": testapp.get_csrf_token()},
            status=200,
        )
        # the user.uid value can't be known ahead, but it will be > 0
        assert response.json["user"]
        assert response.json["match"] == match.uid

    def t_startExpiredMatch(self, testapp):
        one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
        match = Match(expires=one_hour_ago).create()
        testapp.post_json(
            "/play/start",
            {"match": match.uid},
            headers={"X-CSRF-Token": testapp.get_csrf_token()},
            status=400,
        )

    def t_invitedUserHasPlayedGameAlreadyMoreThanAllowed(self, testapp):
        match = Match().create()
        user = User(private=match.is_restricted).create(uhash="acde48001122")
        question = Question(text="1+1 is = to", position=0).save()
        Reaction(question=question, user=user, match=match).create()

        testapp.post_json(
            "/play/start",
            {"match": match.uid, "user": user.uid},
            headers={"X-CSRF-Token": testapp.get_csrf_token()},
            status=400,
        )

    def t_startMatch(self, testapp):
        match = Match().create()
        game = Game(match_uid=match.uid).create()
        question = Question(game_uid=game.uid, text="1+1 is = to", position=0).save()
        user = User().create()

        response = testapp.post_json(
            "/play/start",
            {"match": match.uid, "user": user.uid},
            headers={"X-CSRF-Token": testapp.get_csrf_token()},
            status=200,
        )
        assert response.json["question"] == question.json
        assert response.json["answers"] == []
        assert response.json["user"]

    def t_answerQuestion(self, testapp, trivia_match):
        match = trivia_match
        user = User().create()
        question = match.questions[0][0]
        answer = question.answers_by_position[0]

        response = testapp.post_json(
            "/play/next",
            {"question": question.uid, "answer": answer.uid, "user": user.uid},
            headers={"X-CSRF-Token": testapp.get_csrf_token()},
            status=200,
        )
        assert response.json["question"] == question.json
        assert response.json["answers"] == []
        assert response.json["user"] == user.uid
