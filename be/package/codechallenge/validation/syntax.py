land_play_schema = {"match_uid": {"type": "integer", "coerce": int}}

start_play_schema = {
    "match_uid": {"type": "integer", "coerce": int},
    "user_uid": {"type": "integer", "coerce": int},
}

next_play_schema = {
    "match_uid": {"type": "integer", "coerce": int, "required": True},
    "user_uid": {"type": "integer", "coerce": int, "required": True},
    "answer_uid": {"type": "integer", "coerce": int, "required": True},
    "question_uid": {"type": "integer", "coerce": int, "required": True},
}

create_question_schema = {
    "game_uid": {"type": "integer", "coerce": int, "required": False},
    "text": {"type": "string", "required": True, "maxlength": 400},
    "position": {"type": "integer", "coerce": int, "required": True},
    "time": {"type": "integer", "coerce": int},
    "content_url": {"type": "string", "coerce": str},
    "code": {"type": "string", "coerce": str},
}

edit_question_schema = {
    "question_uid": {"type": "integer", "coerce": int, "required": True},
    "game_uid": {"type": "integer", "coerce": int, "required": False},
    "text": {"type": "string", "required": True, "maxlength": 400},
    "position": {"type": "integer", "coerce": int, "required": True},
    "time": {"type": "integer", "coerce": int},
    "content_url": {"type": "string", "coerce": str},
    "code": {"type": "string", "coerce": str},
}


create_match_schema = {
    "name": {"type": "string", "coerce": str},
    "questions": {
        "type": "list",
        "schema": {
            "type": "dict",
            "schema": {
                "text": {"type": "string"},
                "answers": {
                    "type": "list",
                    "schema": {"type": "dict", "schema": {"text": {"type": "string"}}},
                },
            },
        },
        "required": True,
    },
}


edit_match_schema = {"match_uid": {"type": "integer"}}
