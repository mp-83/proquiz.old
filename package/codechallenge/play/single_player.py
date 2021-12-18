from codechallenge.models import Reaction


class PlayException(Exception):
    """"""


class SinglePlayer:
    def __init__(self, user):
        self.user = user
        self._current_question = None
        self._current_match = None
        self._current_game = None

    def start(self, match):
        self._current_match = match
        game = match.first_game()
        self._current_game = game
        self._current_question = game.first_question()
        return self._current_question

    @property
    def current_question(self):
        return self._current_question

    @property
    def next_question(self):
        _next = None
        if not self._current_match:
            return _next

        for q in self._current_game.questions:
            if q.position == self._current_question.position + 1:
                _next = q
        return _next

    def react(self, answer):
        Reaction(
            question_uid=self._current_question.uid,
            answer_uid=answer.uid,
            user_uid=self.user.uid,
        ).create()
        return self.next_question

    def game_is_over(self):
        return self.next_question is None

    @property
    def next_game(self):
        _next = None
        if not self._current_game:
            return _next

        for g in self._current_match.games:
            if g.index == self._current_game.index + 1:
                _next = g
        return _next

    def match_is_over(self):
        return self.next_game is None

    def match_started(self):
        return self._current_match is not None

    def current_game(self):
        if not self.match_started:
            raise PlayException("Match not started")
        return self._current_game
