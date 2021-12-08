import pytest
from codechallenge.app import StoreConfig
from codechallenge.db import count
from codechallenge.models import Answer, Game, Question, User
from sqlalchemy.exc import IntegrityError, InvalidRequestError


class TestCaseConfigSingleton:
    def t_singletonHasToBeCreatedOnce(self):
        sc = StoreConfig()
        settings_mock = {"setting": True}
        sc.config = settings_mock
        for _ in range(2):
            assert sc is StoreConfig()
            assert sc.config is settings_mock


class TestCaseModels:
    def t_countMethodReturnsTheCorrectValue(self, fillTestingDB):
        assert count(Question) == 3

    def t_theQuestionAtPosition(self, fillTestingDB):
        question = Question().at_position(1)
        assert question.text == "q1.text"
        assert question.create_timestamp is not None

    def t_newCreatedAnswersShouldBeAvailableFromTheQuestion(self, fillTestingDB):
        question = Question().at_position(1)
        Answer(question=question, text="question2.answer1", position=1).create()
        Answer(question=question, text="question2.answer2", position=2).create()
        assert count(Answer) == 2
        assert question.answers[0].question_uid == question.uid

    def t_editingTextOfExistingQuestion(self, fillTestingDB):
        question = Question().at_position(2)
        question.update(text="new-text")
        assert question.text == "new-text"

    def t_createQuestionWithoutPosition(self, fillTestingDB):
        new_question = Question(text="new-question").save()
        assert new_question.position == 4
        assert new_question.is_open

    def t_allAnswersOfAQuestionMustDiffer(self, fillTestingDB):
        question = Question().at_position(2)
        with pytest.raises((IntegrityError, InvalidRequestError)):
            question.answers.extend(
                [
                    Answer(text="question2.answer1", position=1),
                    Answer(text="question2.answer1", position=2),
                ]
            )
            question.save()

        current_session = StoreConfig().session
        current_session.rollback

    def t_createNewUserAndSetPassword(self, dbsession):
        new_user = User(email="user@test.project").create()
        new_user.set_password("password")
        new_user.save()
        assert new_user.check_password("password")
        assert new_user.create_timestamp is not None

    def t_questionMustBeBoundToAGame(self, dbsession):
        new_question = Question(text="new-question").save()
        assert new_question.game is not None

    def t_gameMustBeBoundToAMatch(self, dbsession):
        new_game = Game(index=1).create()
        assert new_game.match is not None
        assert new_game.match.name != ""

    def t_raiseErrorWhenTwoGamesOfMatchHaveSamePosition(self, dbsession):
        new_game = Game(index=1).create()
        with pytest.raises((IntegrityError, InvalidRequestError)):
            Game(index=1, match_uid=new_game.match.uid).create()
