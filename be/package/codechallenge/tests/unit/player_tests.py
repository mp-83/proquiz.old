import pytest
from codechallenge.exceptions import EmptyMatchError
from codechallenge.models import Answer, Game, Match, Question, Reactions, User
from codechallenge.play.single_player import SinglePlayer


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

    def t_anyQuestionShouldBeLinkedToAGameWhenMatchStarts(self, dbsession):
        match = Match().create()
        user = User(email="user@test.project").create()

        player = SinglePlayer(user)
        with pytest.raises(EmptyMatchError):
            player.start(match)


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
