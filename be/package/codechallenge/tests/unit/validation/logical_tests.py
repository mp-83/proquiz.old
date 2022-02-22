import pytest
from codechallenge.exceptions import ValidateError
from codechallenge.validation.logical import ValidatePlayNext


class TestCaseNextEndPoint:
    def t_cannotAcceptSameReactionAgain(self):
        # despite the delay between the two (which respects the DB constraint)
        pass

    def t_answerDoesNotBelongToQuestion(self, dbsession):
        with pytest.raises(ValidateError):
            ValidatePlayNext(answer_uid=1, question_uid=1).valid_answer()

    def t_answerDoesNotExists(self, dbsession):
        with pytest.raises(ValidateError):
            ValidatePlayNext(answer_id=10000).valid_answer()

    def t_userDoesNotExists(self):
        pass

    def t_matchDoesNotExists(self):
        pass
