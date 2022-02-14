from codechallenge.entities import Reaction, Reactions
from codechallenge.exceptions import (
    EmptyMatchError,
    GameError,
    GameOver,
    MatchNotPlayableError,
    MatchOver,
)


class PlayException(Exception):
    """"""


class QuestionFactory:
    def __init__(self, game, counter=0):
        self._game = game
        self._counter = counter
        self._question = None

    def next_question(self):
        if (not self._game.questions and self._counter == 0) or (
            self._counter == len(self._game.questions)
        ):
            raise GameOver(f"Game {self._game} has not questions")

        if self._game.order:
            self._question = self._game.ordered_questions[self._counter]
        else:
            self._question = self._game.questions[self._counter]

        self._counter += 1
        return self._question

    @property
    def current(self):
        return self._question

    @property
    def counter(self):
        return self._counter

    @property
    def is_last_question(self):
        return self._counter == len(self._game.questions)


class GameFactory:
    def __init__(self, match):
        self._match = match
        self._counter = -1
        self._game = None

    @property
    def counter(self):
        return self._counter

    @property
    def games(self):
        if self._match.order:
            return self._match.ordered_games
        return self._match.games

    def next_game(self):
        if not self.games:
            raise EmptyMatchError(f"Match {self._match.name} contains no Game")

        if self._counter == len(self.games) - 1:
            raise MatchOver(f"Match {self._match.name}")

        self._counter += 1
        return self.current

    @property
    def current(self):
        self._game = self.games[self._counter]
        return self._game

    @property
    def match_started(self):
        return self._game is not None

    @property
    def is_last_game(self):
        return self._counter == len(self.games) - 1


class SinglePlayer:
    def __init__(self, user, match):
        self._user = user
        self._current_match = match
        self._current_game = None
        self._game_factory = GameFactory(match)
        self._question_factory = None
        self._current_reaction = None

    def start(self):
        self._current_match.refresh()
        if self._current_match.left_attempts(self._user) == 0:
            raise MatchNotPlayableError(
                f"User {self._user} has no left attempts for Match {self._current_match.name}"
            )

        self._current_game = self.next_game()
        self._question_factory = QuestionFactory(self.current_game)
        question = self.next_question()
        self._current_reaction = Reaction(
            match_uid=self._current_match.uid,
            question_uid=question.uid,
            user_uid=self._user.uid,
            game_uid=self._current_game.uid,
        ).create()

        # left as sanity check. To be removed after testing
        assert self._current_game.uid == question.game.uid

        return question

    @property
    def current_question(self):
        return self._question_factory.current

    @property
    def match_started(self):
        return self._game_factory.match_started

    @property
    def current_game(self):
        return self._game_factory.current

    @property
    def can_be_resumed(self):
        return self._game_factory

    def last_reaction(self, question):
        reactions = Reactions.all_reactions_of_user_to_match(
            self._user, self._current_match
        ).filter_by(_answer=None)

        if reactions.count() > 0:
            return reactions.first()

        return Reaction(
            match_uid=self._current_match.uid,
            question_uid=question.uid,
            game_uid=question.game.uid,
            user_uid=self._user.uid,
        ).create()

    @property
    def match_can_be_resumed(self):
        """Determine if this match can be restored

        By counting the reactions it is possible to
        determine if all questions were displayed
        """
        m = self._current_match
        return m.is_restricted and len(m.reactions) < len(m.questions)

    def react(self, answer):
        if not self._current_reaction:
            self._current_reaction = self.last_reaction(answer.question)
            self._game_factory = GameFactory(self._current_match)
            self._question_factory = QuestionFactory(self.current_game, counter=2)

        self._current_reaction.record_answer(answer)
        _question = self.next_question()
        return _question

    def next_question(self):
        if not self.current_game:
            raise GameError(f"Match {self._current_match.name} is not started")

        try:
            return self._question_factory.next_question()
        except GameOver:
            self._current_game = self.next_game()

    def next_game(self):
        return self._game_factory.next_game()
