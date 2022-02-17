import pytest
from codechallenge.entities import (
    Answer,
    Game,
    Match,
    Question,
    Reaction,
    Reactions,
    User,
)
from codechallenge.exceptions import (
    GameError,
    GameOver,
    MatchError,
    MatchNotPlayableError,
    MatchOver,
)
from codechallenge.play.single_player import (
    GameFactory,
    PlayerStatus,
    QuestionFactory,
    SinglePlayer,
)


class TestCaseQuestionFactory:
    def t_nextQuestionWhenNotOrdered(self, dbsession):
        match = Match().create()
        game = Game(match_uid=match.uid, index=1, order=False).create()
        q_berlin = Question(
            text="Where is Berlin?", game_uid=game.uid, position=0
        ).save()
        q_zurich = Question(
            text="Where is Zurich?", game_uid=game.uid, position=1
        ).save()

        question_factory = QuestionFactory(game, *())
        assert question_factory.next() == q_berlin
        assert question_factory.next() == q_zurich
        assert question_factory.current == q_zurich

    def t_nextQuestionWhenOrdered(self, dbsession):
        """Questions are inversely created
        to make the ordering meaningful.
        """
        match = Match().create()
        game = Game(match_uid=match.uid, index=1).create()
        second = Question(text="Where is London?", game_uid=game.uid, position=1).save()
        first = Question(text="Where is Paris?", game_uid=game.uid, position=0).save()

        question_factory = QuestionFactory(game, *())
        assert question_factory.next() == first
        assert question_factory.next() == second

    def t_gameOverWhenThereAreNoQuestions(self, dbsession):
        match = Match().create()
        game = Game(match_uid=match.uid, index=1).create()

        question_factory = QuestionFactory(game, *())
        with pytest.raises(GameOver):
            question_factory.next()

    def t_gameIsOverAfterLastQuestion(self, dbsession):
        match = Match().create()
        game = Game(match_uid=match.uid, index=1).create()
        Question(text="Where is Paris?", game_uid=game.uid, position=0).save()

        question_factory = QuestionFactory(game, *())
        question_factory.next()
        with pytest.raises(GameOver):
            question_factory.next()

    def t_isLastQuestion(self, dbsession):
        match = Match().create()
        game = Game(match_uid=match.uid, index=1).create()
        Question(text="Where is Amsterdam?", game_uid=game.uid, position=0).save()
        Question(text="Where is Lion?", game_uid=game.uid, position=1).save()

        question_factory = QuestionFactory(game)
        question_factory.next()
        assert not question_factory.is_last_question
        question_factory.next()
        assert question_factory.is_last_question

    def t_previousQuestion(self, dbsession):
        match = Match().create()
        game = Game(match_uid=match.uid, index=1).create()
        first = Question(
            text="Where is Amsterdam?", game_uid=game.uid, position=0
        ).save()
        Question(text="Where is Lion?", game_uid=game.uid, position=1).save()

        question_factory = QuestionFactory(game)
        question_factory.next()
        question_factory.next()
        assert question_factory.previous() == first

    def t_callingPreviousWithoutNext(self, dbsession):
        match = Match().create()
        game = Game(match_uid=match.uid, index=1).create()
        Question(text="Where is Amsterdam?", game_uid=game.uid, position=0).save()
        Question(text="Where is Lion?", game_uid=game.uid, position=1).save()

        question_factory = QuestionFactory(game)
        with pytest.raises(GameError):
            question_factory.previous()

    def t_callingPreviousRightAfterFirstNext(self, dbsession):
        match = Match().create()
        game = Game(match_uid=match.uid, index=1).create()
        Question(text="Where is Amsterdam?", game_uid=game.uid, position=0).save()
        Question(text="Where is Lion?", game_uid=game.uid, position=1).save()

        question_factory = QuestionFactory(game)
        question_factory.next()
        with pytest.raises(GameError):
            question_factory.previous()


class TestCaseGameFactory:
    def t_nextGameWhenOrdered(self, dbsession):
        match = Match(order=True).create()
        second = Game(match_uid=match.uid, index=2).create()
        first = Game(match_uid=match.uid, index=1).create()

        game_factory = GameFactory(match, *())
        assert game_factory.next() == first
        assert game_factory.next() == second

    def t_matchWithoutGamesThrowsError(self, dbsession):
        match = Match().create()
        game_factory = GameFactory(match, *())

        with pytest.raises(MatchOver):
            game_factory.next()

        dbsession.rollback()

    def t_matchStarted(self, dbsession):
        match = Match().create()
        Game(match_uid=match.uid, index=1).create()
        game_factory = GameFactory(match, *())

        assert not game_factory.match_started

    def t_isLastGame(self, dbsession):
        match = Match().create()
        Game(match_uid=match.uid, index=0).create()
        Game(match_uid=match.uid, index=1).create()
        game_factory = GameFactory(match, *())

        game_factory.next()
        assert not game_factory.is_last_game
        game_factory.next()
        assert game_factory.is_last_game

    def t_nextOverTwoSessions(self, dbsession):
        match = Match().create()
        g1 = Game(match_uid=match.uid, index=0).create()
        Game(match_uid=match.uid, index=1).create()
        game_factory = GameFactory(match, g1.uid)

        game_factory.next()
        assert game_factory.is_last_game

    def t_callingPreviousRightAfterFirstNext(self, dbsession):
        match = Match().create()
        Game(match_uid=match.uid, index=0).create()
        Game(match_uid=match.uid, index=1).create()
        game_factory = GameFactory(match, *())

        game_factory.next()
        with pytest.raises(MatchError):
            game_factory.previous()

    def t_callingPreviousWithoutNext(self, dbsession):
        match = Match().create()
        Game(match_uid=match.uid, index=0).create()
        Game(match_uid=match.uid, index=1).create()
        game_factory = GameFactory(match, *())

        with pytest.raises(MatchError):
            game_factory.previous()


class TestCaseStatus:
    def t_questionsDisplayed(self, dbsession, emitted_queries):
        match = Match().create()
        game = Game(match_uid=match.uid, index=0).create()
        q1 = Question(text="Where is Miami", position=0, game=game).save()
        q2 = Question(text="Where is London", position=1, game=game).save()
        q3 = Question(text="Where is Paris", position=2, game=game).save()
        user = User(email="user@test.project").create()

        Reaction(match=match, question=q1, user=user, game_uid=game.uid).create()

        Reaction(match=match, question=q2, user=user, game_uid=game.uid).create()
        Reaction(
            match=Match().create(), question=q3, user=user, game_uid=game.uid
        ).create()
        status = PlayerStatus(user, match)
        before = len(emitted_queries)
        assert status.questions_displayed() == {q2.uid: q2, q1.uid: q1}
        assert len(emitted_queries) == before + 1

    def t_questionDisplayedByGame(self, dbsession):
        match = Match().create()
        game = Game(match_uid=match.uid, index=0).create()
        q1 = Question(text="Where is Miami", position=0, game=game).save()
        q2 = Question(text="Where is London", position=1, game=game).save()
        q3 = Question(text="Where is Paris", position=2, game=game).save()
        user = User(email="user@test.project").create()

        Reaction(match=match, question=q1, user=user, game_uid=game.uid).create()

        Reaction(match=match, question=q2, user=user, game_uid=game.uid).create()
        Reaction(
            match=Match().create(), question=q3, user=user, game_uid=game.uid
        ).create()
        status = PlayerStatus(user, match)
        assert status.questions_displayed_by_game(game) == {q2.uid: q2, q1.uid: q1}


class TestCaseSinglePlayerSingleGame:
    def t_reactionIsCreatedAsSoonAsQuestionIsReturned(self, dbsession):
        match = Match().create()
        first_game = Game(match_uid=match.uid, index=1).create()
        question = Question(
            text="Where is London?", game_uid=first_game.uid, position=0
        ).save()
        user = User(email="user@test.project").create()

        player = SinglePlayer(user, match)
        question_displayed = player.start()

        assert question_displayed == question
        assert player.current_question == question_displayed
        assert Reactions.count() == 1

    def t_reactToFirstQuestion(self, dbsession):
        match = Match().create()
        first_game = Game(match_uid=match.uid, index=1).create()
        first = Question(
            text="Where is London?", game_uid=first_game.uid, position=0
        ).save()
        answer = Answer(question=first, text="UK", position=1).create()
        second = Question(
            text="Where is Paris?", game_uid=first_game.uid, position=1
        ).save()
        user = User(email="user@test.project").create()

        player = SinglePlayer(user, match)
        player.start()
        next_q = player.react(answer)

        reaction = user.reactions[0]
        assert reaction.q_counter == 0
        assert reaction.g_counter == 0

        assert next_q == second

    def t_matchCannotBePlayedMoreThanMatchTimes(self, dbsession):
        match = Match().create()
        user = User(email="user@test.project").create()
        game = Game(match_uid=match.uid, index=1).create()
        question = Question(
            text="Where is London?", game_uid=game.uid, position=0
        ).save()

        player = SinglePlayer(user, match)
        assert player.start() == question

        with pytest.raises(MatchNotPlayableError):
            player.start()

        assert match.reactions
        dbsession.rollback()

    def t_matchOver(self, dbsession):
        match = Match().create()
        first_game = Game(match_uid=match.uid, index=0).create()
        question = Question(
            text="Where is London?", game_uid=first_game.uid, position=0
        ).save()
        answer = Answer(question=question, text="UK", position=1).create()
        user = User(email="user@test.project").create()

        player = SinglePlayer(user, match)
        player.start()
        with pytest.raises(MatchOver):
            player.react(answer)

    def t_playMatchOverMultipleRequests(self, dbsession):
        # the SinglePlayer is instanced multiple times
        match = Match().create()
        first_game = Game(match_uid=match.uid, index=1, order=False).create()
        first = Question(
            text="Where is London?", game_uid=first_game.uid, position=0
        ).save()
        first_answer = Answer(question=first, text="UK", position=1).create()
        second = Question(
            text="Where is Paris?", game_uid=first_game.uid, position=1
        ).save()
        second_answer = Answer(question=first, text="France", position=1).create()
        third = Question(
            text="Where is Dublin?", game_uid=first_game.uid, position=2
        ).save()
        third_answer = Answer(question=first, text="Ireland", position=1).create()

        user = User(email="user@test.project").create()

        player = SinglePlayer(user, match)
        assert player.start() == first
        next_q = player.react(first_answer)
        assert next_q == second

        player = SinglePlayer(user, match)
        next_q = player.react(second_answer)

        # assert user.reactions[0].question == second
        assert next_q == third
        player = SinglePlayer(user, match)
        player.react(third_answer)


class TestCaseResumeMatch:
    def t_matchCanBeResumedWhenThereIsStillOneQuestionToDisplay(self, dbsession):
        match = Match().create()
        first_game = Game(match_uid=match.uid, index=0).create()
        question = Question(
            text="Where is London?", game_uid=first_game.uid, position=0
        ).save()
        Question(text="Where is Moscow?", game_uid=first_game.uid, position=1).save()
        answer = Answer(question=question, text="UK", position=1).create()
        user = User(email="user@test.project").create()

        player = SinglePlayer(user, match)
        player.start()
        player.react(answer)
        assert player.match_can_be_resumed

    def t_matchCanNotBeResumedBecausePublic(self, dbsession):
        match = Match(is_restricted=False).create()
        user = User(email="user@test.project").create()

        player = SinglePlayer(user, match)
        assert not player.match_can_be_resumed
