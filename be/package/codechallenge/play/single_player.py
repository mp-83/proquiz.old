from codechallenge.exceptions import EmptyMatchError
from codechallenge.models import Reaction


class PlayException(Exception):
    """"""


class SinglePlayer:
    def __init__(self, user, match):
        self._user = user
        self._current_question = None
        self._current_match = match
        self._current_game = None

    def start(self):
        game = self.next_game()
        if not game:
            raise EmptyMatchError(f"Match {self._current_match.name} contains no Game")

        self._current_game = game
        self._current_question = game.first_question()
        self._current_reaction = Reaction(
            question_uid=self._current_question.uid,
            user_uid=self._user.uid,
        ).create()
        return self._current_question

    @property
    def current_question(self):
        return self._current_question

    def next_question(self):
        _next = None
        if not self._current_game:
            return _next

        for q in self._current_game.questions:
            if q.position == self._current_question.position + 1:
                _next = q
        return _next

    def react(self, answer):
        self._current_reaction.record_answer(answer)
        return self.next_question()

    def game_is_over(self):
        return self.next_question() is None

    def next_game(self):
        for g in self._current_match.games:
            if not self._current_game and g.index == 1:
                self._current_game = g
                return g
            if g.index == self._current_game.index + 1:
                self._current_game = g
                return g

    def match_is_over(self):
        return self.next_question() is None

    def match_started(self):
        return self._current_question is not None

    def current_game(self):
        if not self.match_started:
            raise PlayException("Match not started")
        return self._current_game
