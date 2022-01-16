import pytest
from codechallenge.exceptions import (
    EmptyMatchError,
    GameError,
    GameOver,
    MatchNotPlayableError,
    MatchOver,
)
from codechallenge.models import Answer, Game, Match, Question, Reactions, User
from codechallenge.play.single_player import GameFactory, QuestionFactory, SinglePlayer


class TestCaseQuestionFactory:
    def t_nextQuestionWhenNotOrdered(self, dbsession):
        match = Match().create()
        game = Game(match_uid=match.uid, index=1, order=False).create()
        q_berlin = Question(
            text="Where is Berlin?", game_uid=game.uid, position=2
        ).save()
        q_zurich = Question(
            text="Where is Zurich?", game_uid=game.uid, position=1
        ).save()

        factory = QuestionFactory(game)
        assert factory.next_question() == q_berlin
        assert factory.next_question() == q_zurich
        assert factory.current == q_zurich

    def t_nextQuestionWhenOrdered(self, dbsession):
        """Questions are inversely created
        to make the ordering meaningful.
        """
        match = Match().create()
        game = Game(match_uid=match.uid, index=1).create()
        second = Question(text="Where is London?", game_uid=game.uid, position=2).save()
        first = Question(text="Where is Paris?", game_uid=game.uid, position=1).save()

        factory = QuestionFactory(game)
        assert factory.next_question() == first
        assert factory.next_question() == second

    def t_gameOver(self, dbsession):
        match = Match().create()
        game = Game(match_uid=match.uid, index=1).create()

        factory = QuestionFactory(game)
        with pytest.raises(GameOver):
            factory.next_question()

    def t_gameIsOverAfterLastQuestion(self, dbsession):
        match = Match().create()
        game = Game(match_uid=match.uid, index=1).create()
        Question(text="Where is Paris?", game_uid=game.uid, position=1).save()

        factory = QuestionFactory(game)
        factory.next_question()
        with pytest.raises(GameOver):
            factory.next_question()


class TestCaseGameFactory:
    def t_nextGameWhenOrdered(self, dbsession):
        match = Match(order=True).create()
        second = Game(match_uid=match.uid, index=2).create()
        first = Game(match_uid=match.uid, index=1).create()

        factory = GameFactory(match)
        assert factory.next_game() == first
        assert factory.next_game() == second

    def t_matchWithoutGamesThrowsError(self, dbsession):
        match = Match().create()
        factory = GameFactory(match)

        with pytest.raises(EmptyMatchError):
            factory.next_game()

        dbsession.rollback()

    def t_matchStarted(self, dbsession):
        match = Match().create()
        Game(match_uid=match.uid, index=1).create()
        factory = GameFactory(match)

        assert not factory.match_started


class TestCaseSinglePlayerSingleGame:
    def t_reactionIsCreatedAsSoonAsQuestionIsReturned(self, dbsession):
        match = Match().create()
        first_game = Game(match_uid=match.uid, index=1).create()
        question = Question(text="Where is London?", game_uid=first_game.uid).save()
        user = User(email="user@test.project").create()

        player = SinglePlayer(user, match)
        question_displayed = player.start()

        assert question_displayed == question
        assert player.current_question == question_displayed
        assert Reactions.count() == 1

    def t_reactToOneOpenQuestion(self, dbsession):
        match = Match().create()
        first_game = Game(match_uid=match.uid, index=1).create()
        question = Question(text="Where is London?", game_uid=first_game.uid).save()
        second = Question(text="Where is Paris?", game_uid=first_game.uid).save()
        answer = Answer(question=question, text="UK", position=1).create()
        user = User(email="user@test.project").create()

        player = SinglePlayer(user, match)
        player.start()
        next_q = player.react(answer)
        assert Reactions.count() == 1
        assert next_q == second

    def t_callingNextQuestionWhenMatchIsNotStarted(self, dbsession):
        match = Match().create()
        user = User(email="user@test.project").create()
        Game(match_uid=match.uid, index=1).create()
        player = SinglePlayer(user, match)

        with pytest.raises(GameError) as err:
            player.next_question()

        assert err.value.message == f"Match {match.name} is not started"

        dbsession.rollback()

    def t_matchCannotBePlayedMoreThanMatchTimes(self, dbsession):
        match = Match().create()
        user = User(email="user@test.project").create()
        game = Game(match_uid=match.uid, index=1).create()
        question = Question(text="Where is London?", game_uid=game.uid).save()

        player = SinglePlayer(user, match)
        assert player.start() == question

        with pytest.raises(MatchNotPlayableError):
            player.start()

        assert match.reactions
        dbsession.rollback()
