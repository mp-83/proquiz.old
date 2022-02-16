from codechallenge.entities import Reaction, Reactions
from codechallenge.exceptions import (
    GameError,
    GameOver,
    MatchError,
    MatchNotPlayableError,
    MatchOver,
)


# TODO is this used anywhere?
class PlayException(Exception):
    """"""


class QuestionFactory:
    def __init__(self, game, *displayed_ids):
        self._game = game
        # displayed_ids are ordered based on their display order
        self.displayed_ids = displayed_ids
        self._question = None

    def next(self):
        questions = (
            self._game.ordered_questions if self._game.order else self._game.questions
        )
        for q in questions:
            if q.uid not in self.displayed_ids:
                self._question = q
                self.displayed_ids += (q.uid,)
                return q

        raise GameOver(f"Game {self._game} has no questions")

    def previous(self):
        # remember that the reaction is not deleted
        questions = (
            self._game.ordered_questions if self._game.order else self._game.questions
        )
        for q in questions:
            if not self._question or len(self.displayed_ids) == 1:
                continue

            if q.uid == self.displayed_ids[-2]:
                self._question = q
                return q

        msg = (
            "No questions were displayed"
            if not self.displayed_ids
            else "Only one question was displayed"
        )
        raise GameError(f"{msg} for Game {self._game}")

    @property
    def current(self):
        return self._question

    @property
    def is_last_question(self):
        questions = (
            self._game.ordered_questions if self._game.order else self._game.questions
        )
        return len(self.displayed_ids) == len(questions)


class GameFactory:
    def __init__(self, match, *played_ids):
        self._match = match
        self.played_ids = played_ids
        self._game = None

    def next(self):
        games = self._match.ordered_games if self._match.order else self._match.games
        for g in games:
            if g.uid not in self.played_ids:
                self.played_ids += (g.uid,)
                self._game = g
                return g

        raise MatchOver(f"Match {self._match.name}")

    def previous(self):
        games = self._match.ordered_games if self._match.order else self._match.games
        for g in games:
            if not self._game or len(self.played_ids) == 1:
                continue

            if g.uid == self.played_ids[-2]:
                self._game = g
                return g

        msg = (
            "No game were played" if not self.played_ids else "Only one game was played"
        )
        raise MatchError(f"{msg} for Match {self._match.name}")

    @property
    def current(self):
        return self._game

    @property
    def match_started(self):
        return len(self.played_ids) > 0

    @property
    def is_last_game(self):
        games = self._match.ordered_games if self._match.order else self._match.games
        return len(self.played_ids) == len(games)


class SinglePlayer:
    def __init__(self, user, match):
        self._user = user
        self._current_match = match
        self._game_factory = None
        self._question_factory = None
        self._current_reaction = None

    def start(self):
        self._current_match.refresh()
        if self._current_match.left_attempts(self._user) == 0:
            raise MatchNotPlayableError(
                f"User {self._user} has no left attempts for Match {self._current_match.name}"
            )

        self._game_factory = GameFactory(self._current_match)
        _game = self.next_game()
        self._question_factory = QuestionFactory(_game)
        question = self.next_question()

        # left as sanity check. To be removed after testing
        assert _game.uid == question.game.uid

        self._current_reaction = Reaction(
            match_uid=self._current_match.uid,
            question_uid=question.uid,
            user_uid=self._user.uid,
            game_uid=_game.uid,
            q_counter=0,
            g_counter=0,
        ).create()

        return question

    @property
    def match_started(self):
        return self._game_factory.match_started

    @property
    def current_game(self):
        return self._game_factory.current

    def next_game(self):
        return self._game_factory.next_game()

    @property
    def can_be_resumed(self):
        return self._game_factory

    def last_reaction(self, question):
        reactions = Reactions.all_reactions_of_user_to_match(
            self._user, self._current_match
        ).filter_by(
            _answer=None
        )  # TODO to fix: or _open_answer=None

        if reactions.count() > 0:
            return reactions.first()

        return Reaction(
            match_uid=self._current_match.uid,
            question_uid=question.uid,
            game_uid=question.game.uid,
            user_uid=self._user.uid,
            q_counter=0,
            g_counter=0,
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
            self._game_factory = GameFactory(
                self._current_match, self._current_reaction.g_counter + 1
            )
            self._question_factory = QuestionFactory(
                self.current_game, self._current_reaction.q_counter + 1
            )
            # import pdb;pdb.set_trace()

        # counters are incremented to be used in the next reaction
        self._current_reaction.q_counter = self._question_factory.counter
        self._current_reaction.g_counter = self._game_factory.counter
        self._current_reaction.record_answer(answer)

        # import pdb;pdb.set_trace()

        _question = self.next_question()
        return _question

    @property
    def current_question(self):
        return self._question_factory.current

    def next_question(self):
        if not self.current_game:
            raise GameError(f"Match {self._current_match.name} is not started")

        try:
            return self._question_factory.next_question()
        except GameOver:
            self._current_game = self.next_game()
