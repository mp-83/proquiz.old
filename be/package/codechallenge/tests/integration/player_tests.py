from datetime import datetime, timedelta, timezone

from codechallenge.entities import Game, Match, Question
from codechallenge.entities.user import UserFactory


class TestCaseBadRequest:
    def t_endpoints(self, testapp):
        endpoints = ["/play/BAD", "/play/start", "/play/next"]
        for endpoint in endpoints:
            try:
                testapp.post_json(
                    endpoint,
                    {"match_uid": None},
                    headers={"X-CSRF-Token": testapp.get_csrf_token()},
                    status=400,
                )
            # TODO: to replace with specific exception
            except Exception as err:
                assert not err


class TestCasePlayLand:
    # the test scenario for land/404 is already tested above
    def t_playLand(self, testapp):
        match = Match(with_hash=True).save()
        response = testapp.post(
            f"/play/{match.uhash}",
            headers={"X-CSRF-Token": testapp.get_csrf_token()},
            status=200,
        )
        # the user.uid value can't be known ahead, but it will be > 0
        assert response.json["user"]
        assert response.json["match"] == match.uid


class TestCasePlayCode:
    def t_playCode(self, testapp):
        in_one_hour = datetime.now() + timedelta(hours=1)
        match = Match(with_code=True, expires=in_one_hour).save()
        response = testapp.post_json(
            "/play/code",
            {"match_code": match.code},
            headers={"X-CSRF-Token": testapp.get_csrf_token()},
            status=200,
        )
        # the user.uid value can't be known ahead, but it will be > 0
        assert response.json["user"]
        assert response.json["match"] == match.uid


class TestCasePlayStart:
    def t_unexistentMatch(self, testapp):
        testapp.post_json(
            "/play/start",
            {"match_uid": 100, "user_uid": 1},
            headers={"X-CSRF-Token": testapp.get_csrf_token()},
            status=404,
        )

    def t_startExpiredMatch(self, testapp):
        one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
        match = Match(expires=one_hour_ago).save()
        user = UserFactory(signed=match.is_restricted).fetch()
        testapp.post_json(
            "/play/start",
            {"match_uid": match.uid, "user_uid": user.uid},
            headers={"X-CSRF-Token": testapp.get_csrf_token()},
            status=400,
        )

    def t_startMatch(self, testapp):
        match = Match(is_restricted=False).save()
        game = Game(match_uid=match.uid).save()
        question = Question(game_uid=game.uid, text="1+1 is = to", position=0).save()
        user = UserFactory(signed=match.is_restricted).fetch()

        response = testapp.post_json(
            "/play/start",
            {"match_uid": match.uid, "user_uid": user.uid},
            headers={"X-CSRF-Token": testapp.get_csrf_token()},
            status=200,
        )
        assert response.json["question"] == question.json
        assert response.json["answers"] == []
        assert response.json["user"]

    def _startMatchWithoutQuestion(self, testapp):
        match = Match(is_restricted=False).save()
        Game(match_uid=match.uid).save()
        user = UserFactory(signed=match.is_restricted).fetch()

        response = testapp.post_json(
            "/play/start",
            {"match_uid": match.uid, "user_uid": user.uid},
            headers={"X-CSRF-Token": testapp.get_csrf_token()},
            status=200,
        )
        assert response.json["user"]

    # the password feature is tested more thoroughly in the logical tests
    def t_startRestrictedMatchUsingPassword(self, testapp):
        match = Match(is_restricted=True).save()
        game = Game(match_uid=match.uid).save()
        question = Question(game_uid=game.uid, text="1+1 is = to", position=0).save()
        user = UserFactory(signed=match.is_restricted).fetch()

        response = testapp.post_json(
            "/play/start",
            {"match_uid": match.uid, "user_uid": user.uid, "password": match.password},
            headers={"X-CSRF-Token": testapp.get_csrf_token()},
            status=200,
        )

        assert response.json["question"] == question.json


class TestCasePlayNext:
    def t_duplicateSameReaction(self, testapp, trivia_match):
        match = trivia_match
        user = UserFactory(signed=match.is_restricted).fetch()
        question = match.questions[0][0]
        answer = question.answers_by_position[0]

        testapp.post_json(
            "/play/next",
            {
                "match_uid": match.uid,
                "question_uid": question.uid,
                "answer_uid": answer.uid,
                "user_uid": user.uid,
            },
            headers={"X-CSRF-Token": testapp.get_csrf_token()},
            status=200,
        )
        testapp.post_json(
            "/play/next",
            {
                "match_uid": match.uid,
                "question_uid": question.uid,
                "answer_uid": answer.uid,
                "user_uid": user.uid,
            },
            headers={"X-CSRF-Token": testapp.get_csrf_token()},
            status=400,
        )

    def t_unexistentQuestion(self, testapp):
        testapp.post_json(
            "/play/next",
            {
                "match_uid": 1,
                "question_uid": 1,
                "answer_uid": 1,
                "user_uid": 1,
            },
            headers={"X-CSRF-Token": testapp.get_csrf_token()},
            status=404,
        )

    def t_answerQuestion(self, testapp, trivia_match):
        match = trivia_match
        user = UserFactory(signed=match.is_restricted).fetch()
        question = match.questions[0][0]
        answer = question.answers_by_position[0]

        response = testapp.post_json(
            "/play/next",
            {
                "match_uid": match.uid,
                "question_uid": question.uid,
                "answer_uid": answer.uid,
                "user_uid": user.uid,
            },
            headers={"X-CSRF-Token": testapp.get_csrf_token()},
            status=200,
        )
        assert response.json["question"] == match.questions[0][1].json
        assert response.json["user"] == user.uid
