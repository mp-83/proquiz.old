from codechallenge.exceptions import EmptyMatchError, GameError, MatchNotPlayableError
from codechallenge.models import Reaction


class PlayException(Exception):
    """"""


class SinglePlayer:
    def __init__(self, user, match):
        self._user = user
        self._current_match = match
        self._current_question = None
        self._current_game = None
        self._question_counter = 1

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

    def next_question(self):
        if not self._current_game:
            raise GameError(f"Unexistent game for match {self._current_match}")

        self._current_question = self._current_game.ordered_questions[
            self._question_counter
        ]
        self._question_counter += 1

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
