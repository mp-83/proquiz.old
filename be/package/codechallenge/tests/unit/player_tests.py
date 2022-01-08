import pytest
from codechallenge.exceptions import EmptyMatchError
from codechallenge.models import Answer, Game, Match, Question, Reactions, User
from codechallenge.play.single_player import SinglePlayer


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

    def t_reactToTimedQuestionInTime(self, dbsession):
        match = Match().create()
        first_game = Game(match_uid=match.uid, index=1).create()
        question = Question(
            text="Where is Oslo?", game_uid=first_game.uid, time=2
        ).save()
        answer = Answer(question=question, text="Norway", position=1).create()
        user = User(email="user@test.project").create()

        player = SinglePlayer(user, match)
        player.start()
        player.react(answer)
        reaction = Reactions.reaction_of_user_to_question(question=question, user=user)
        assert reaction.answer
        assert reaction.answer_time

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

    def t_nextQuestionProperty(self, dbsession):
        match = Match().create()
        first_game = Game(match_uid=match.uid, index=1).create()
        Question(text="Where is London?", game_uid=first_game.uid).save()
        second = Question(text="Where is Paris?", game_uid=first_game.uid).save()
        user = User(email="user@test.project").create()

        player = SinglePlayer(user, match)
        player.start()
        assert player.next_question() == second

    def t_whenNoQuestionsAreLeftGameIsOver(self, dbsession):
        match = Match().create()
        first_game = Game(match_uid=match.uid, index=1).create()
        question = Question(text="Where is London?", game_uid=first_game.uid).save()
        answer = Answer(question=question, text="UK", position=1).create()
        user = User(email="user@test.project").create()

        player = SinglePlayer(user, match)
        player.start()
        player.react(answer)
        assert player.game_is_over()

    def t_whenThereAreNoQuestionGameIsOver(self, dbsession):
        match = Match().create()
        Game(match_uid=match.uid, index=1).create()
        user = User(email="user@test.project").create()

        player = SinglePlayer(user, match)
        assert player.game_is_over()

    def t_whenLastGameIsOverAlsoMatchIsOver(self, dbsession):
        match = Match().create()
        Game(match_uid=match.uid, index=1).create()
        user = User(email="user@test.project").create()

        player = SinglePlayer(user, match)
        assert player.match_is_over()

    def t_nextGameButMatchIsEmpty(self, dbsession):
        match = Match().create()
        user = User(email="user@test.project").create()

        player = SinglePlayer(user, match)
        assert player.next_game() is None

    def t_nextGame(self, dbsession):
        match = Match().create()
        user = User(email="user@test.project").create()
        player = SinglePlayer(user, match)
        first_game = Game(match_uid=match.uid, index=1).create()
        second_game = Game(match_uid=match.uid, index=2).create()

        assert player.next_game() == first_game
        assert player.next_game() == second_game

    def t_matchWithoutGamesThrowsError(self, dbsession):
        match = Match().create()
        user = User(email="user@test.project").create()
        player = SinglePlayer(user, match)
        with pytest.raises(EmptyMatchError):
            player.start()


class TestCaseSinglePlayerMultipleGames:
    def t_matchStarted(self, dbsession):
        match = Match().create()
        Game(match_uid=match.uid, index=1).create()
        user = User(email="user@test.project").create()

        player = SinglePlayer(user, match)
        assert not player.match_started()
