from codechallenge.entities import Game, Match, Question
from codechallenge.tests.fixtures import TEST_1


class TestCasePlay:
    def startGame(self, testapp, trivia_match):
        new_match = Match().create()
        new_game = Game(match_uid=new_match.uid).create()
        for position, question in enumerate(TEST_1):
            new = Question(
                game_uid=new_game.uid, text=question["text"], position=position
            )
            new.create_with_answers(question.get("answers"))

        response = testapp.post_json(
            "/play/start",
            {"match": new_match.uid},
            headers={"X-CSRF-Token": testapp.get_csrf_token()},
            status=200,
        )
        assert response
