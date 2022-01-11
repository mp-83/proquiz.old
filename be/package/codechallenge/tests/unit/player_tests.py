import pytest
from codechallenge.exceptions import EmptyMatchError, GameError, MatchNotPlayableError
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

    @pytest.mark.skip("")
    def t_whenNoQuestionsAreLeftGameIsOver(self, dbsession):
        match = Match().create()
        first_game = Game(match_uid=match.uid, index=1).create()
        question = Question(text="Where is London?", game_uid=first_game.uid).save()
        answer = Answer(question=question, text="UK", position=1).create()
        user = User(email="user@test.project").create()

        player = SinglePlayer(user, match)
        player.start()
        player.react(answer)
        assert player.game_is_over

    @pytest.mark.skip("")
    def t_whenThereAreNoQuestionGameIsOver(self, dbsession):
        match = Match().create()
        Game(match_uid=match.uid, index=1).create()
        user = User(email="user@test.project").create()

        player = SinglePlayer(user, match)
        with pytest.raises(GameError):
            player.start()

        assert player.game_is_over

    def t_whenLastGameIsOverAlsoMatchIsOver(self, dbsession):
        match = Match().create()
        Game(match_uid=match.uid, index=1).create()
        user = User(email="user@test.project").create()

        player = SinglePlayer(user, match)
        assert player.match_is_over

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

    def t_nextQuestion(self, dbsession):
        match = Match().create()
        user = User(email="user@test.project").create()
        game = Game(match_uid=match.uid, index=1).create()
        question_1 = Question(text="Where is London?", game_uid=game.uid).save()
        question_2 = Question(text="Where is Lisboa?", game_uid=game.uid).save()
        player = SinglePlayer(user, match)
        player.next_game()

        player.next_question()
        assert player.current_question == question_1
        player.next_question()
        assert player.current_question == question_2

    def t_nextQuestionWhenGameIsEmpty(self, dbsession):
        match = Match().create()
        user = User(email="user@test.project").create()
        Game(match_uid=match.uid, index=1).create()
        player = SinglePlayer(user, match)

        with pytest.raises(GameError) as err:
            player.next_question()

        assert err.value.message == f"Unexistent game for match {match}"

        dbsession.rollback()

    def t_matchWithoutGamesThrowsError(self, dbsession):
        match = Match().create()
        user = User(email="user@test.project").create()
        player = SinglePlayer(user, match)
        with pytest.raises(EmptyMatchError):
            player.start()

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

    def t_matchStarted(self, dbsession):
        match = Match().create()
        Game(match_uid=match.uid, index=1).create()
        user = User(email="user@test.project").create()

        player = SinglePlayer(user, match)
        assert not player.match_started()
