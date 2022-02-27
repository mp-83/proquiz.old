import pytest
from codechallenge.entities import (
    Answer,
    Game,
    Match,
    Question,
    Questions,
    Reaction,
    User,
)
from codechallenge.exceptions import NotFoundObjectError, ValidateError
from codechallenge.validation.logical import (
    RetrieveObject,
    ValidatePlayNext,
    ValidatePlayStart,
)


class TestCaseRetrieveObject:
    def t_objectNotFound(self, dbsession):
        with pytest.raises(NotFoundObjectError):
            RetrieveObject(uid=1, otype="match").get()

    def t_objectIsOfCorrectType(self, dbsession):
        user = User().save()
        obj = RetrieveObject(uid=1, otype="user").get()
        assert obj == user


class TestCaseStartEndPoint:
    def t_publicUserRestrictedMatch(self, dbsession):
        match = Match(is_restricted=True).save()
        user = User(email="user@test.project").save()
        with pytest.raises(ValidateError):
            ValidatePlayStart(match=match.uid, user=user.uid).is_valid()

    def t_userDoesNotExists(self, dbsession):
        with pytest.raises(NotFoundObjectError):
            ValidatePlayStart(user=1).valid_user()


class TestCaseNextEndPoint:
    def t_cannotAcceptSameReactionAgain(self, dbsession):
        # despite the delay between the two (which respects the DB constraint)
        match = Match().save()
        game = Game(match_uid=match.uid, index=0).save()
        question = Question(
            text="Where is London?", game_uid=game.uid, position=0
        ).save()
        answer = Answer(question=question, text="UK", position=1).save()
        user = User(email="user@test.project").save()

        Reaction(
            match=match,
            question=question,
            user=user,
            game_uid=game.uid,
            answer_uid=answer.uid,
        ).save()

        with pytest.raises(ValidateError):
            ValidatePlayNext(user=user.uid, question=question.uid).valid_reaction()

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
