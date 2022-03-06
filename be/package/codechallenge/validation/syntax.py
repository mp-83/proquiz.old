from codechallenge.constants import (
    CODE_POPULATION,
    HASH_POPULATION,
    MATCH_CODE_LEN,
    MATCH_HASH_LEN,
    MATCH_PASSWORD_LEN,
    PASSWORD_POPULATION,
)

land_play_schema = {
    "match_uhash": {
        "type": "string",
        "required": True,
        "regex": "[" + f"{HASH_POPULATION}" + "]{" + f"{MATCH_HASH_LEN}" + "}",
    }
}


code_play_schema = {
    "match_code": {
        "type": "string",
        "required": True,
        "regex": "[" + f"{CODE_POPULATION}" + "]{" + f"{MATCH_CODE_LEN}" + "}",
    }
}


start_play_schema = {
    "match_uid": {"type": "integer", "coerce": int, "required": True, "min": 1},
    "user_uid": {"type": "integer", "coerce": int, "required": True, "min": 1},
    "password": {
        "type": "string",
        "regex": "[" + f"{PASSWORD_POPULATION}" + "]{" + f"{MATCH_PASSWORD_LEN}" + "}",
    },
}

next_play_schema = {
    "match_uid": {"type": "integer", "coerce": int, "required": True, "min": 1},
    "user_uid": {"type": "integer", "coerce": int, "required": True, "min": 1},
    "answer_uid": {"type": "integer", "coerce": int, "required": True, "min": 1},
    "question_uid": {"type": "integer", "coerce": int, "required": True, "min": 1},
}

create_question_schema = {
    "game_uid": {"type": "integer", "coerce": int, "required": False},
    "text": {"type": "string", "required": True, "maxlength": 400},
    "position": {"type": "integer", "coerce": int, "required": True},
    "time": {"type": "integer", "coerce": int},
    "content_url": {"type": "string", "coerce": str},
    "code": {"type": "string", "coerce": str},
    "answers": {
        "type": "list",
        "schema": {
            "type": "dict",
            "schema": {"text": {"type": "string", "required": True}},
        },
    },
}

edit_question_schema = {
    "game_uid": {"type": "integer", "coerce": int, "required": False},
    "text": {"type": "string", "maxlength": 400},
    "position": {"type": "integer", "coerce": int, "min": 0},
    "time": {"type": "integer", "coerce": int},
    "content_url": {"type": "string", "coerce": str},
    "code": {"type": "string", "coerce": str},
    "answers": {
        "type": "list",
        "schema": {
            "type": "dict",
            "schema": {
                "uid": {"type": "integer", "coerce": int, "required": False},
                "text": {"type": "string", "required": True},
            },
        },
    },
}


def coerce_order(value):
    if value in ["false", "False", False]:
        return False
    elif value in ["true", "True", True]:
        return True
    return None


def coerce_times(value):
    if value == "null":
        return None
    return value


create_match_schema = {
    "name": {"type": "string"},
    # coerce callables are executed according to the order they are in the tuple
    "times": {
        "type": "integer",
        "coerce": (coerce_times, int),
        "min": 1,
        "nullable": True,
    },
    "is_restricted": {"type": "boolean", "coerce": bool},
    "order": {"type": "boolean", "coerce": coerce_order},
    "questions": {
        "type": "list",
        "schema": {
            "type": "dict",
            "schema": {
                "text": {"type": "string", "required": True},
                "answers": {
                    "type": "list",
                    "schema": {
                        "type": "dict",
                        "schema": {"text": {"type": "string", "required": True}},
                    },
                },
            },
        },
    },
}


edit_match_schema = {
    "name": {"type": "string"},
    "times": {"type": "integer", "coerce": int, "min": 1, "nullable": True},
    "is_restricted": {"type": "boolean", "coerce": bool},
    "order": {"type": "boolean", "coerce": coerce_order},
    "questions": {
        "type": "list",
        "schema": {
            "type": "dict",
            "schema": {
                "text": {"type": "string"},
                "game": {"type": "integer", "coerce": int, "min": 0},
                "answers": {
                    "type": "list",
                    "schema": {"type": "dict", "schema": {"text": {"type": "string"}}},
                },
            },
        },
    },
}

# TODO: verify why is not working
# 'regex': '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+.[a-zA-Z0-9-.]{2:}$'
user_login_schema = {
    "email": {"type": "string", "required": True, "minlength": 5, "maxlength": 30},
    "password": {"type": "string", "required": True, "minlength": 8, "maxlength": 100},
}
