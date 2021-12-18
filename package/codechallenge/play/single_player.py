from codechallenge.models import Reaction


class SinglePlayer:
    def __init__(self, user):
        self.user = user
        self._current_question = None

    def start(self, match):
        game = match.first_game()
        self._current_question = game.first_question()
        return self._current_question

    @property
    def current_question(self):
        return self._current_question

    def react(self, answer):
        Reaction(
            question_uid=self._current_question.uid,
            answer_uid=answer.uid,
            user_uid=self.user.uid,
        ).create()
        return
