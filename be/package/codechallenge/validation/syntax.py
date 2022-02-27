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
    "game_uid": {"type": "integer", "coerce": int, "required": True},
    "text": {"type": "string", "required": True, "maxlength": 400},
    "position": {"type": "integer", "coerce": int, "required": True},
    "time": {"type": "integer", "coerce": int},
    "content_url": {"type": "string", "coerce": int},
    "code": {"type": "string"},
}

edit_question_schema = {}
