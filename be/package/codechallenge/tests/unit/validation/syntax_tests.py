from cerberus import Validator
from codechallenge.validation.syntax import (
    create_question_schema,
    edit_question_schema,
    land_play_schema,
    next_play_schema,
    start_play_schema,
)


class TestCasePlaySchemas:
    def t_matchUidAsNone(self):
        v = Validator(land_play_schema)
        is_valid = v.validate({"match_uid": None})
        assert not is_valid

    def t_validStartPayload(self):
        v = Validator(start_play_schema)
        is_valid = v.validate({"match_uid": 1, "user_uid": 1})
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

    def t_newQuestionData(self):
        v = Validator(create_question_schema)
        is_valid = v.validate(
            {"game_uid": "1", "text": "".join("a" for _ in range(400)), "position": 1}
        )
        assert is_valid

    def t_editQuestion(self):
        v = Validator(edit_question_schema)
        is_valid = v.validate(
            {"game_uid": "1", "text": "".join("a" for _ in range(400)), "position": 1}
        )
        assert is_valid
