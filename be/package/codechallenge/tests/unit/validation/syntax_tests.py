import pytest
from cerberus import Validator
from codechallenge.validation.syntax import (
    code_play_schema,
    create_match_schema,
    create_question_schema,
    edit_match_schema,
    edit_question_schema,
    land_play_schema,
    next_play_schema,
    start_play_schema,
    user_login_schema,
)


class TestCasePlaySchemas:
    def t_matchUidAsNone(self):
        v = Validator(land_play_schema)
        is_valid = v.validate({"match_uhash": "IJD34KOP"})
        assert not is_valid
        assert v.errors == {"match_uhash": ["Wrong hash length"]}

    def t_matchWrongCode(self):
        v = Validator(code_play_schema)
        is_valid = v.validate({"match_code": "34569"})
        assert not is_valid
        assert v.errors == {"match_code": ["value does not match regex '[0-9]{4}'"]}

    def t_validStartPayloadWithoutPassword(self):
        v = Validator(start_play_schema)
        is_valid = v.validate({"match_uid": 1, "user_uid": 1})
        assert is_valid

    def t_startPayloadWithPassword(self):
        v = Validator(start_play_schema)
        is_valid = v.validate({"match_uid": 1, "user_uid": 1, "password": "KDVBG"})
        assert is_valid

    def t_validNextPayload(self):
        v = Validator(next_play_schema)
        is_valid = v.validate(
            {"match_uid": 1, "user_uid": 2, "answer_uid": 3, "question_uid": 4}
        )
        assert is_valid

    def t_allRequiredByDefault(self):
        v = Validator(next_play_schema)
        is_valid = v.validate(
            {
                "match_uid": 1,
                "user_uid": "2",
                "answer_uid": 3,
            }
        )
        assert not is_valid
        assert v.errors == {"question_uid": ["required field"]}


class TestCaseQuestionSchema:
    def t_templateQuestion(self):
        v = Validator(create_question_schema)
        is_valid = v.validate({"text": "".join("a" for _ in range(400)), "position": 1})
        assert is_valid

    def t_gameQuestion(self):
        v = Validator(create_question_schema)
        is_valid = v.validate(
            {"game_uid": "1", "text": "".join("a" for _ in range(400)), "position": 1}
        )
        assert is_valid

    def t_editQuestion(self):
        v = Validator(edit_question_schema)
        is_valid = v.validate(
            {
                "game_uid": "1",
                "text": "".join("a" for _ in range(400)),
                "position": 1,
            }
        )
        assert is_valid


class TestCaseMatchSchema:
    def t_createPayloadWithQuestions(self):
        v = Validator(create_match_schema)
        is_valid = v.validate(
            {
                "name": "new match",
                "times": "2",
                "is_restricted": "true",
                "questions": [
                    {
                        "text": "Which of the following statements cannot be inferred from the passage?",
                        "answers": [
                            {
                                "text": "The Turk began its tour of Europe in April of 1783."
                            },
                            {
                                "text": "Philidor found his match with the Turk challenging."
                            },
                        ],
                    },
                ],
            }
        )
        assert is_valid
        assert v.document["is_restricted"]

    def t_multipleEdgeValues(self):
        v = Validator(create_match_schema)
        document = {
            "name": "new match",
            "times": "2",
            "is_restricted": "true",
            "order": "false",
            "questions": [{"text": "text"}],
        }
        for value in [1, None, "10", "null"]:
            document.update(times=value)
            is_valid = v.validate(document)
            assert is_valid

    def t_allowForPartialUpdate(self):
        v = Validator(edit_match_schema)
        is_valid = v.validate({"is_restricted": False})
        assert is_valid
        assert not v.document["is_restricted"]


class TestCaseUserSchema:
    def t_emptyUserNameAndPassword(self):
        # arguments are too short
        v = Validator(user_login_schema)
        is_valid = v.validate({"email": "", "password": "pass"})
        assert not is_valid

    @pytest.mark.skip("skipped until regex is activated")
    def t_invalidEmail(self):
        v = Validator(user_login_schema)
        is_valid = v.validate({"email": "e@a.c", "password": "password"})
        assert not is_valid
