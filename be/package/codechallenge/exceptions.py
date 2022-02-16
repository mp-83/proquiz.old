class BaseException(Exception):
    def __init__(self, message, *args):
        super(Exception).__init__(*args)
        self._message = message

    @property
    def message(self):
        return self._message


class NotUsableQuestionError(BaseException):
    """"""


class MatchError(BaseException):
    """"""


class MatchNotPlayableError(BaseException):
    """Match has been played by the user more than match.times"""


class GameError(BaseException):
    """Generic exception occuring during Match"""


class GameOver(BaseException):
    """"""


class MatchOver(BaseException):
    """Match is started but contains not games"""
