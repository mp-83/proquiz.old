from datetime import datetime

import pytest
from codechallenge.app import StoreConfig
from codechallenge.db import count
from codechallenge.models import (
    Answer,
    Game,
    Match,
    Matches,
    Question,
    Reaction,
    Reactions,
    User,
)
from codechallenge.play.single_player import SinglePlayer
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
        current_session.rollback()

    def t_createNewUserAndSetPassword(self, dbsession):
        new_user = User(email="user@test.project").create()
        new_user.set_password("password")
        new_user.save()
        assert new_user.check_password("password")
        assert new_user.create_timestamp is not None

    def t_questionMustBeBoundToAGame(self, dbsession):
        new_question = Question(text="new-question").save()
        assert new_question.game is not None

    def t_createManyQuestionsAtOnce(self, dbsession):
        data = {
            "text": "Following the machine’s debut, Kempelen was reluctant to display the Turk because",
            "answers": [
                {"text": "The machine was undergoing repair"},
                {
                    "text": "He had dismantled it following its match with Sir Robert Murray Keith."
                },
                {"text": "He preferred to spend time on his other projects."},
                {"text": "It had been destroyed by fire."},
            ],
            "position": 1,
        }
        new_question = Question(text=data["text"], position=data["position"])
        new_question.create_with_answers(data["answers"])

        expected = {e["text"] for e in data["answers"]}
        assert new_question
        assert {e.text for e in new_question.answers} == expected
        assert Answer.with_text("The machine was undergoing repair").is_correct


class TestCaseMatchModel:
    def t_questionsPropertyReturnsTheExpectedResults(self, dbsession):
        match = Match().create()
        first_game = Game(match_uid=match.uid, index=1).create()
        Question(text="Where is London?", game_uid=first_game.uid).save()
        second_game = Game(match_uid=match.uid, index=2).create()
        Question(text="Where is Vienna?", game_uid=second_game.uid).save()
        assert match.questions[0].text == "Where is London?"
        assert match.questions[1].text == "Where is Vienna?"

    def t_matchWithName(self, dbsession):
        original = Match().create()
        found = Matches.with_name(original.name)
        assert found == original


class TestCaseGameModel:
    def t_gameMustBeBoundToAMatch(self, dbsession):
        new_game = Game().create()
        assert new_game.match is not None
        assert new_game.match.name != ""

    def t_raiseErrorWhenTwoGamesOfMatchHaveSamePosition(self, dbsession):
        new_game = Game(index=1).create()
        with pytest.raises((IntegrityError, InvalidRequestError)):
            Game(index=1, match_uid=new_game.match.uid).create()

        dbsession.rollback()


class TestCaseReactionModel:
    def t_cannotExistsTwoReactionsOfTheSameUserAtSameTime(self, dbsession):
        user = User(email="user@test.project").create()
        question = Question(text="new-question").save()
        answer = Answer(
            question=question, text="question2.answer1", position=1
        ).create()

        now = datetime.now()
        with pytest.raises((IntegrityError, InvalidRequestError)):
            Reaction(
                question=question, answer=answer, user=user, create_timestamp=now
            ).create()
            Reaction(
                question=question, answer=answer, user=user, create_timestamp=now
            ).create()
        dbsession.rollback()

    def t_ifQuestionChangesThenAlsoFKIsUpdatedAndAffectsReaction(self, dbsession):
        user = User(email="user@test.project").create()
        question = Question(text="1+1 is = to").save()
        answer = Answer(question=question, text="2", position=1).create()
        reaction = Reaction(question=question, answer=answer, user=user).create()
        question.text = "1+2 is = to"
        question.save()

        assert reaction.question.text == "1+2 is = to"


class TestCaseSinglePlayerSingleGame:
    def t_startGame(self, dbsession):
        match = Match().create()
        first_game = Game(match_uid=match.uid, index=1).create()
        question = Question(text="Where is London?", game_uid=first_game.uid).save()
        user = User(email="user@test.project").create()

        player = SinglePlayer(user)
        question_displayed = player.start(match)
        assert question_displayed == question

    def t_currentQuestion(self, dbsession):
        match = Match().create()
        first_game = Game(match_uid=match.uid, index=1).create()
        question = Question(text="Where is London?", game_uid=first_game.uid).save()
        user = User(email="user@test.project").create()

        player = SinglePlayer(user)
        player.start(match)
        assert player.current_question == question

    def t_reactToOneQuestion(self, dbsession):
        match = Match().create()
        first_game = Game(match_uid=match.uid, index=1).create()
        question = Question(text="Where is London?", game_uid=first_game.uid).save()
        second = Question(text="Where is Paris?", game_uid=first_game.uid).save()
        answer = Answer(question=question, text="UK", position=1).create()
        user = User(email="user@test.project").create()

        player = SinglePlayer(user)
        player.start(match)
        next_q = player.react(answer)
        assert Reactions.count() == 1
        assert next_q == second

    def t_nextQuestionProperty(self, dbsession):
        match = Match().create()
        first_game = Game(match_uid=match.uid, index=1).create()
        Question(text="Where is London?", game_uid=first_game.uid).save()
        second = Question(text="Where is Paris?", game_uid=first_game.uid).save()
        user = User(email="user@test.project").create()

        player = SinglePlayer(user)
        player.start(match)
        assert player.next_question == second

    def t_whenNoQuestionsAreLeftGameIsOver(self, dbsession):
        match = Match().create()
        first_game = Game(match_uid=match.uid, index=1).create()
        question = Question(text="Where is London?", game_uid=first_game.uid).save()
        answer = Answer(question=question, text="UK", position=1).create()
        user = User(email="user@test.project").create()

        player = SinglePlayer(user)
        player.start(match)
        player.react(answer)
        assert player.game_is_over()

    def t_whenThereAreNoQuestionGameIsOver(self, dbsession):
        match = Match().create()
        Game(match_uid=match.uid, index=1).create()
        user = User(email="user@test.project").create()

        player = SinglePlayer(user)
        assert player.game_is_over()
        assert player.match_is_over()


class TestCaseSinglePlayerMultipleGames:
    def t_nextGame(self, dbsession):
        match = Match().create()
        Game(match_uid=match.uid, index=1).create()
        second_game = Game(match_uid=match.uid, index=2).create()
        user = User(email="user@test.project").create()

        player = SinglePlayer(user)
        player.start(match)
        assert player.next_game == second_game

    def t_matchStarted(self, dbsession):
        match = Match().create()
        Game(match_uid=match.uid, index=1).create()
        user = User(email="user@test.project").create()

        player = SinglePlayer(user)
        assert not player.match_started()

    def t_currentGame(self, dbsession):
        match = Match().create()
        current = Game(match_uid=match.uid, index=1).create()
        user = User(email="user@test.project").create()

        player = SinglePlayer(user)
        player.start(match)
        assert player.current_game() == current
