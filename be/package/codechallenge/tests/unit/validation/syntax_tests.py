from datetime import datetime

from cerberus import Validator
from codechallenge.validation.syntax import (
    code_play_schema,
    create_match_schema,
    create_question_schema,
    edit_match_schema,
    edit_question_schema,
    land_play_schema,
    match_yaml_import_schema,
    next_play_schema,
    sign_play_schema,
    start_play_schema,
    user_login_schema,
)


class TestCaseNullable:
    def t_nullableValues(self):
        for schema, field in [
            (land_play_schema, "match_uhash"),
            (code_play_schema, "match_code"),
        ]:
            v = Validator(schema)
            is_valid = v.validate({field: None})
            assert not is_valid
            assert v.errors[field][0].startswith("null value not allowed")


class TestCasePlaySchemas:
    def t_matchUHashCannotBeNone(self):
        v = Validator(land_play_schema)
        is_valid = v.validate({"match_uhash": "IJD34KOP"})
        assert not is_valid
        assert v.errors["match_uhash"][0].startswith("value does not match regex")

    def t_matchWrongCode(self):
        v = Validator(code_play_schema)
        is_valid = v.validate({"match_code": "34569"})
        assert not is_valid
        assert v.errors["match_code"][0].startswith("value does not match regex")

    def t_validStartPayloadWithoutUser(self):
        v = Validator(start_play_schema)
        is_valid = v.validate({"match_uid": 1})
        assert is_valid

    def t_validStartPayloadWithoutPassword(self):
        v = Validator(start_play_schema)
        is_valid = v.validate({"match_uid": 1, "user_uid": 1})
        assert is_valid

    def t_startPayloadWithPassword(self):
        v = Validator(start_play_schema)
        is_valid = v.validate({"match_uid": 1, "user_uid": 1, "password": "KDVBG"})
        assert not is_valid
        assert v.errors["password"][0].startswith("value does not match regex")

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

    def t_emailAndBirthDate(self):
        v = Validator(sign_play_schema)
        is_valid = v.validate({"email": "user@pp.com", "token": "12022021"})
        assert is_valid

    def t_invalidBirthDateNull(self):
        v = Validator(sign_play_schema)
        is_valid = v.validate({"email": "user@pp.com", "token": None})
        assert not is_valid
        assert v.errors == {"token": ["null value not allowed"]}

    def t_invalidEmailNull(self):
        v = Validator(sign_play_schema)
        is_valid = v.validate({"email": None, "token": "11012014"})
        assert not is_valid
        assert v.errors == {"email": ["null value not allowed"]}


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

    def t_expirationValuesCannotBeNone(self):
        v = Validator(create_match_schema)
        document = {
            "name": "new match",
            "with_code": "true",
            "questions": [],
            "to_time": None,
            "from_time": None,
        }
        is_valid = v.validate(document)
        assert not is_valid
        assert v.errors == {
            "from_time": ["null value not allowed"],
            "to_time": ["null value not allowed"],
        }

    def t_expirationValuesMustBeDatetimeIsoFormatted(self):
        v = Validator(create_match_schema)
        is_valid = v.validate(
            {
                "name": "new match",
                "times": "2",
                "with_code": "true",
                "questions": [],
                "from_time": "2022-03-19T16:10:39.135166",
                "to_time": "2022-03-19T16:10:39.935155",
            }
        )
        assert is_valid
        assert isinstance(v.document["to_time"], datetime)

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

    def t_validYamlContent(self, valid_encoded_yaml_content):
        v = Validator(match_yaml_import_schema)
        is_valid = v.validate({"match_uid": 1, "data": valid_encoded_yaml_content})
        assert is_valid
        assert v.document["data"] == {
            "questions": [
                "Where is Adelaide?",
                {"answers": ["Australia", "Japan", "Kenya"]},
            ]
        }

    def t_invalidYamlContent(self, faulty_encoded_yaml_content):
        v = Validator(match_yaml_import_schema)
        is_valid = v.validate({"match_uid": 1, "data": faulty_encoded_yaml_content})
        assert not is_valid
        assert (
            "cannot be coerced: while parsing a block collection" in v.errors["data"][0]
        )

    def t_invalidContentPadding(self, faulty_encoded_yaml_content):
        v = Validator(match_yaml_import_schema)
        is_valid = v.validate(
            {"match_uid": 1, "data": faulty_encoded_yaml_content[:-1]}
        )
        assert not is_valid
        assert "cannot be coerced: Incorrect padding" in v.errors["data"][0]

    def t_invalidDataValues(self):
        v = Validator(match_yaml_import_schema)
        document = {"match_uid": 1}
        for value in [None, ""]:
            document.update(data=value)
            is_valid = v.validate(document)
            assert not is_valid


class TestCaseUserSchema:
    def t_emptyUserNameAndPassword(self):
        # arguments are too short
        v = Validator(user_login_schema)
        is_valid = v.validate({"email": "", "password": "pass"})
        assert not is_valid

    def t_invalidEmail(self):
        v = Validator(user_login_schema)
        is_valid = v.validate({"email": "e@a.c", "password": "password"})
        assert not is_valid
