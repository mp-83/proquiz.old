from codechallenge.exceptions import (
    EmptyMatchError,
    GameError,
    GameOver,
    MatchNotPlayableError,
    MatchOver,
)
from codechallenge.models import Reaction


class PlayException(Exception):
    """"""


class QuestionFactory:
    def __init__(self, game):
        self._game = game
        self._counter = 1
        self._question = None

    def next_question(self):
        if self._game.order:
            self._question = self._game.ordered_questions[self._counter]
        else:
            self._question = self._game.questions[self._counter - 1]

        self._counter += 1
        return self._question

    @property
    def current(self):
        return self._question


class SinglePlayer:
    def __init__(self, user, match):
        self._user = user
        self._current_match = match
        self._current_question = None
        self._current_game = None
        self._question_counter = 0
        self._game_counter = 0

    def _status_check(self):
        if not self._current_game and self._game_counter == 0:
            raise EmptyMatchError("")
        if not self._current_question and self._question_counter == 0:
            raise GameOver("")

    def start(self):
        self._current_match.refresh()

        if self._current_match.left_attempts(self._user) == 0:
            raise MatchNotPlayableError(
                f"User {self._user} has no left attempts for Match {self._current_match.name}"
            )

        self.next_game()
        if not self._current_game:
            raise EmptyMatchError(f"Match {self._current_match.name} contains no Game")

        self.next_question()
        self._current_reaction = Reaction(
            match_uid=self._current_match.uid,
            question_uid=self._current_question.uid,
            user_uid=self._user.uid,
        ).create()
        return self._current_question

    @property
    def current_question(self):
        return self._current_question

    def react(self, answer):
        self._current_reaction.record_answer(answer)
        self.next_question()
        return self._current_question

    @property
    def game_is_over(self):
        return self.next_question() is None

    def next_game(self):
        for g in self._current_match.games:
            if not self._current_game and g.index == 1:
                self._current_game = g
                return g
            if self._current_game and g.index == self._current_game.index + 1:
                self._current_game = g
                return g

    def match_is_over(self):
        return self.game_is_over and not self.next_game()

    def match_started(self):
        return self._current_question is not None

    def current_game(self):
        if not self.match_started:
            raise PlayException("Match not started")
        return self._current_game
