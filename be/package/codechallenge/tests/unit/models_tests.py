from datetime import datetime
from math import isclose

import pytest
from codechallenge.app import StoreConfig
from codechallenge.entities import (
    Answer,
    Answers,
    Game,
    Match,
    Matches,
    OpenAnswer,
    Question,
    Questions,
    Reaction,
    Reactions,
    User,
)
from codechallenge.entities.reaction import ReactionScore
from codechallenge.exceptions import NotUsableQuestionError
from sqlalchemy.exc import IntegrityError, InvalidRequestError


class TestCaseUser:
    def t_createNewUserAndSetPassword(self, dbsession):
        new_user = User(email="user@test.project").create()
        new_user.set_password("password")
        new_user.save()
        assert new_user.check_password("password")
        assert new_user.create_timestamp is not None

    def t_createPrivateUser(self, dbsession, mocker):
        invite_hash = "acde48001122"
        new_user = User(private=True).create(invite_hash)
        assert new_user.email == f"priv-{invite_hash}@progame.io"

    def t_createPublicUser(self, dbsession, mocker):
        mocker.patch("codechallenge.entities.user.uuid4", return_value="acde48001122")
        new_user = User().create()
        assert new_user.email == "pub-acde48001122@progame.io"


class TestCaseQuestion:
    def t_theQuestionAtPosition(self, fillTestingDB):
        question = Question().at_position(0)
        assert question.text == "q1.text"
        assert question.create_timestamp is not None

    def t_newCreatedAnswersShouldBeAvailableFromTheQuestion(self, fillTestingDB):
        question = Question().at_position(0)
        Answer(question=question, text="question2.answer1", position=1).create()
        Answer(question=question, text="question2.answer2", position=2).create()
        assert Answers.count() == 2
        assert question.answers[0].question_uid == question.uid

    def t_editingTextOfExistingQuestion(self, fillTestingDB):
        question = Question().at_position(1)
        question.update(text="new-text")
        assert question.text == "new-text"

    def t_createQuestionWithoutPosition(self, fillTestingDB):
        new_question = Question(text="new-question", position=1).save()
        assert new_question.is_open
        assert new_question.is_template

    def t_allAnswersOfAQuestionMustDiffer(self, fillTestingDB):
        question = Question().at_position(1)
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
            "position": 0,
        }
        new_question = Question(text=data["text"], position=data["position"])
        new_question.create_with_answers(data["answers"])

        expected = {e["text"] for e in data["answers"]}
        assert new_question
        assert {e.text for e in new_question.answers} == expected
        assert Answer.with_text("The machine was undergoing repair").is_correct

    def t_cloningQuestion(self, dbsession):
        new_question = Question(text="new-question", position=0).save()
        Answer(
            question_uid=new_question.uid,
            text="The machine was undergoing repair",
            position=0,
        ).create()
        cloned = new_question.clone()
        assert new_question.uid != cloned.uid
        assert new_question.answers[0] != cloned.answers[0]

    def t_questionsAnswersAreOrderedByDefault(self, dbsession):
        # the reverse relation fields .answers is ordered by default
        question = Question(text="new-question", position=0).save()
        Answer(question_uid=question.uid, text="Answer1", position=0).create()
        Answer(question_uid=question.uid, text="Answer2", position=1).create()

        assert question.answers[0].text == "Answer1"
        assert question.answers[1].text == "Answer2"

    def t_updateAnswers(self, dbsession):
        question = Question(text="new-question", position=0).save()
        a1 = Answer(question_uid=question.uid, text="Answer1", position=0).create()
        a2 = Answer(question_uid=question.uid, text="Answer2", position=1).create()
        a3 = Answer(question_uid=question.uid, text="Answer3", position=2).create()

        ans_2_json = a2.json
        ans_2_json.update(text="Answer text 2")
        question.update_answers([a3.json, a1.json, ans_2_json])
        assert question.answers_by_position[0].text == "Answer3"
        assert question.answers_by_position[1].text == "Answer1"
        assert question.answers_by_position[2].text == "Answer text 2"


class TestCaseMatchModel:
    def t_questionsPropertyReturnsTheExpectedResults(self, dbsession):
        match = Match().create()
        first_game = Game(match_uid=match.uid, index=0).create()
        Question(text="Where is London?", game_uid=first_game.uid, position=0).save()
        second_game = Game(match_uid=match.uid, index=1).create()
        Question(text="Where is Vienna?", game_uid=second_game.uid, position=0).save()
        assert match.questions[0][0].text == "Where is London?"
        assert match.questions[0][0].game == first_game
        assert match.questions[1][0].text == "Where is Vienna?"
        assert match.questions[1][0].game == second_game

    def t_matchWithName(self, dbsession):
        original = Match().create()
        found = Matches.with_name(original.name)
        assert found == original

    def t_updateTextExistingQuestion(self, dbsession):
        match = Match().create()
        first_game = Game(match_uid=match.uid, index=1).create()
        question = Question(
            text="Where is London?", game_uid=first_game.uid, position=0
        ).save()

        n = Questions.count()
        match.update_questions(
            [
                {
                    "uid": question.uid,
                    "text": "What is the capital of Norway?",
                }
            ],
        )
        no_new_questions = n == Questions.count()
        assert no_new_questions
        assert question.text == "What is the capital of Norway?"

    def t_createMatchUsingTemplateQuestions(self, dbsession):
        question_ids = [
            Question(text="Where is London?", position=0).save().uid,
            Question(text="Where is Vienna?", position=1).save().uid,
        ]
        Answer(
            question_uid=question_ids[0], text="question2.answer1", position=1
        ).create()

        new_match = Match().create()
        questions_cnt = Questions.count()
        answers_cnt = Answers.count()
        new_match.import_template_questions(*question_ids)
        assert Questions.count() == questions_cnt + 2
        assert Answers.count() == answers_cnt + 0

    def t_cannotAssociateQuestionsUsedInAnotherMatch(self, dbsession):
        match = Match().create()
        first_game = Game(match_uid=match.uid, index=2).create()
        question = Question(
            text="Where is London?", game_uid=first_game.uid, position=3
        ).save()
        question_ids = [question.uid]
        with pytest.raises(NotUsableQuestionError):
            match.import_template_questions(*question_ids)

    def t_matchCannotBePlayedIfAreNoLeftAttempts(self, dbsession):
        match = Match().create()
        Game(match_uid=match.uid, index=2).create()
        user = User(email="user@test.project").create()
        question = Question(text="1+1 is = to", position=0).save()
        Reaction(question=question, user=user, match=match).create()

        assert match.reactions[0].user == user
        assert match.left_attempts(user) == 0


class TestCaseGameModel:
    def t_raiseErrorWhenTwoGamesOfMatchHaveSamePosition(self, dbsession):
        new_match = Match().create()
        new_game = Game(index=1, match_uid=new_match.uid).create()
        with pytest.raises((IntegrityError, InvalidRequestError)):
            Game(index=1, match_uid=new_game.match.uid).create()

        dbsession.rollback()

    def t_orderedQuestionsMethod(self, dbsession, emitted_queries):
        match = Match().create()
        game = Game(match_uid=match.uid, index=1).create()
        question_2 = Question(
            text="Where is London?", game_uid=game.uid, position=1
        ).save()
        question_1 = Question(
            text="Where is Lisboa?", game_uid=game.uid, position=0
        ).save()
        question_4 = Question(
            text="Where is Paris?", game_uid=game.uid, position=3
        ).save()
        question_3 = Question(
            text="Where is Berlin?", game_uid=game.uid, position=2
        ).save()

        assert len(emitted_queries) == 6
        assert game.ordered_questions[0] == question_1
        assert game.ordered_questions[1] == question_2
        assert game.ordered_questions[2] == question_3
        assert game.ordered_questions[3] == question_4
        assert len(emitted_queries) == 7


class TestCaseReactionModel:
    def t_cannotExistsTwoReactionsOfTheSameUserAtSameTime(self, dbsession):
        match = Match().create()
        user = User(email="user@test.project").create()
        question = Question(text="new-question", position=0).save()
        answer = Answer(
            question=question, text="question2.answer1", position=1
        ).create()

        now = datetime.now()
        with pytest.raises((IntegrityError, InvalidRequestError)):
            Reaction(
                match_uid=match.uid,
                question_uid=question.uid,
                answer_uid=answer.uid,
                user_uid=user.uid,
                create_timestamp=now,
            ).create()
            Reaction(
                match_uid=match.uid,
                question_uid=question.uid,
                answer_uid=answer.uid,
                user_uid=user.uid,
                create_timestamp=now,
            ).create()
        dbsession.rollback()

    def t_ifQuestionChangesThenAlsoFKIsUpdatedAndAffectsReaction(self, dbsession):
        match = Match().create()
        user = User(email="user@test.project").create()
        question = Question(text="1+1 is = to", position=0).save()
        answer = Answer(question=question, text="2", position=1).create()
        reaction = Reaction(
            match_uid=match.uid,
            question_uid=question.uid,
            answer_uid=answer.uid,
            user_uid=user.uid,
        ).create()
        question.text = "1+2 is = to"
        question.save()

        assert reaction.question.text == "1+2 is = to"

    def t_whenQuestionIsElapsedAnswerIsNotRecorded(self, dbsession):
        match = Match().create()
        user = User(email="user@test.project").create()
        question = Question(text="3*3 = ", time=0, position=0).save()
        reaction = Reaction(match=match, question=question, user=user).create()

        answer = Answer(question=question, text="9", position=1).create()
        reaction.record_answer(answer)

        assert reaction.answer is None

    def t_recordAnswerInTime(self, dbsession):
        match = Match().create()
        user = User(email="user@test.project").create()
        question = Question(text="1+1 =", time=2, position=0).save()
        reaction = Reaction(match=match, question=question, user=user).create()

        answer = Answer(question=question, text="2", position=1).create()
        reaction.record_answer(answer)

        assert reaction.answer
        assert reaction.answer_time
        # because the score is computed over the response
        # time and this one variates at each tests run
        # isclose is used to avoid brittleness
        assert isclose(reaction.score, 0.999, rel_tol=0.05)

    def t_reactionTimingIsRecordedAlsoForOpenQuestions(self, dbsession):
        match = Match().create()
        user = User(email="user@test.project").create()
        question = Question(text="Where is Miami", position=0).save()
        reaction = Reaction(match=match, question=question, user=user).create()

        open_answer = OpenAnswer(text="Florida").create()
        reaction.record_answer(open_answer)
        assert question.is_open
        assert reaction.answer
        assert reaction.answer_time
        # no score should be computed for open questions
        assert not reaction.score

    def t_allReactionsOfUser(self, dbsession):
        match = Match().create()
        user = User(email="user@test.project").create()
        q1 = Question(text="t1", position=0).save()
        q2 = Question(text="t2", position=1).save()
        r1 = Reaction(match=match, question=q1, user=user).create()
        r2 = Reaction(match=match, question=q2, user=user).create()

        reactions = Reactions.all_reactions_of_user_to_match(
            user, match, asc=False
        ).all()
        assert len(reactions) == 2
        assert reactions[0] == r2
        assert reactions[1] == r1


class TestCaseReactionScore:
    def t_computeWithOnlyOnTiming(self):
        rs = ReactionScore(timing=0.2, question_time=3, answer_level=None)
        assert rs.value() == 0.933

    def t_computeWithTimingAndLevel(self):
        rs = ReactionScore(timing=0.2, question_time=3, answer_level=2)
        assert isclose(rs.value(), 0.93 * 2, rel_tol=0.05)

    def t_computeScoreForOpenQuestion(self):
        rs = ReactionScore(timing=0.2, question_time=None, answer_level=None)
        assert rs.value() == 0
