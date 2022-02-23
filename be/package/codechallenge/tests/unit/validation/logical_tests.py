import pytest
from codechallenge.entities import Answer, Questions
from codechallenge.exceptions import NotFoundObjectError, ValidateError
from codechallenge.validation.logical import ValidatePlayNext


class TestCaseNextEndPoint:
    def t_cannotAcceptSameReactionAgain(self):
        # despite the delay between the two (which respects the DB constraint)
        pass

    def t_answerDoesNotBelongToQuestion(self, fillTestingDB, dbsession):
        # simulate a more realistic case
        question = Questions.get(uid=1)
        answer = Answer(question=question, text="UK", position=1).save()
        with pytest.raises(ValidateError):
            ValidatePlayNext(answer=answer.uid, question=10).valid_answer()

    def t_answerDoesNotExists(self, dbsession):
        with pytest.raises(NotFoundObjectError):
            ValidatePlayNext(answer=10000).valid_answer()

    def t_userDoesNotExists(self, dbsession):
        with pytest.raises(NotFoundObjectError):
            ValidatePlayNext(user=1).valid_user()

    def t_matchDoesNotExists(self, dbsession):
        with pytest.raises(NotFoundObjectError):
            ValidatePlayNext(match=1).valid_match()
