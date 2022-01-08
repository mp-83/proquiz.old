from datetime import datetime

import pytest
from codechallenge.app import StoreConfig
from codechallenge.db import count
from codechallenge.exceptions import NotUsableQuestionError
from codechallenge.models import (
    Answer,
    Answers,
    Game,
    Match,
    Matches,
    Question,
    Questions,
    Reaction,
    User,
)
from sqlalchemy.exc import IntegrityError, InvalidRequestError


class TestCaseQuestion:
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
        assert new_question.is_open
        assert new_question.is_template

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

    def t_cloningQuestion(self, dbsession):
        new_question = Question(text="new-question").save()
        Answer(
            question_uid=new_question.uid,
            text="The machine was undergoing repair",
            position=1,
        ).create()
        cloned = new_question.clone()
        assert new_question.uid != cloned.uid
        assert new_question.answers[0] != cloned.answers[0]


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

    def t_createMatchUsingTemplateQuestions(self, dbsession):
        question_ids = [
            Question(text="Where is London?").save().uid,
            Question(text="Where is Vienna?").save().uid,
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


class TestCaseGameModel:
    def t_raiseErrorWhenTwoGamesOfMatchHaveSamePosition(self, dbsession):
        new_match = Match().create()
        new_game = Game(index=1, match_uid=new_match.uid).create()
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
        reaction = Reaction(
            question=question,
            answer=answer,
            user=user,
        ).create()
        question.text = "1+2 is = to"
        question.save()

        assert reaction.question.text == "1+2 is = to"

    # TODO reuse this test for something more useful
    def t_computeReactionTiming(self, dbsession):
        user = User(email="user@test.project").create()
        question = Question(text="1+1 is = to").save()
        reaction = Reaction(question=question, user=user).create()

        answer = Answer(question=question, text="2", position=1).create()
        reaction.record_answer(answer)

        assert reaction.answer_time
