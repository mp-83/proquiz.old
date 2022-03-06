import logging

from cerberus import Validator
from codechallenge.entities import User, Users
from codechallenge.exceptions import NotFoundObjectError, ValidateError
from codechallenge.play.single_player import PlayerStatus, SinglePlayer
from codechallenge.validation.logical import (
    ValidatePlayCode,
    ValidatePlayLand,
    ValidatePlayNext,
    ValidatePlayStart,
)
from codechallenge.validation.syntax import (
    code_play_schema,
    land_play_schema,
    next_play_schema,
    start_play_schema,
)
from pyramid.response import Response
from pyramid.view import view_config

logger = logging.getLogger(__name__)


class PlayEndPoints:
    def __init__(self, request):
        self.request = request

    @view_config(route_name="land", request_method="POST")
    def land(self):
        user = None
        user_input = self.request.matchdict
        v = Validator(land_play_schema)
        if not v.validate(user_input):
            return Response(status=400, json=v.errors)

        try:
            data = ValidatePlayLand(**user_input).is_valid()
        except (NotFoundObjectError, ValidateError) as e:
            if isinstance(e, NotFoundObjectError):
                return Response(status=404)
            return Response(status=400, json={"error": e.message})

        match = data.get("match")
        if match.is_restricted:
            user = Users.get_private_user(mhash=data.get("uhash"))

        if not user:
            user = User(private=match.is_restricted).save()

        return Response(json={"match": match.uid, "user": user.uid})

    @view_config(route_name="code", request_method="POST")
    def code(self):
        user_input = getattr(self.request, "json", None)
        v = Validator(code_play_schema)
        if not v.validate(user_input):
            return Response(status=400, json=v.errors)

        try:
            data = ValidatePlayCode(**user_input).is_valid()
        except (NotFoundObjectError, ValidateError) as e:
            if isinstance(e, NotFoundObjectError):
                return Response(status=404)
            return Response(status=400, json={"error": e.message})

        match = data.get("match")
        user = User(private=True).save()
        return Response(json={"match": match.uid, "user": user.uid})

    @view_config(route_name="start", request_method="POST")
    def start(self):
        user_input = getattr(self.request, "json", None)
        v = Validator(start_play_schema)
        if not v.validate(user_input):
            return Response(status=400, json=v.errors)

        try:
            data = ValidatePlayStart(**v.document).is_valid()
        except (NotFoundObjectError, ValidateError) as e:
            if isinstance(e, NotFoundObjectError):
                return Response(status=404)
            return Response(status=400, json={"error": e.message})

        match = data.get("match")
        user = data.get("user")
        status = PlayerStatus(user, match)
        player = SinglePlayer(status, user, match)
        current_question = player.start()
        match_data = {
            "question": current_question.json,
            "answers": [a.json for a in current_question.answers],
            "user": user.uid,
        }
        return Response(json=match_data)

    @view_config(route_name="next", request_method="POST")
    def next(self):
        user_input = getattr(self.request, "json", None)
        v = Validator(next_play_schema)
        if not v.validate(user_input):
            return Response(status=400, json=v.errors)

        try:
            data = ValidatePlayNext(**user_input).is_valid()
        except (NotFoundObjectError, ValidateError) as e:
            if isinstance(e, NotFoundObjectError):
                return Response(status=404)
            return Response(status=400, json={"error": e.message})

        match = data.get("match")
        user = data.get("user")
        answer = data.get("answer")

        status = PlayerStatus(user, match)
        player = SinglePlayer(status, user, match)
        next_q = player.react(answer)

        return Response(json={"question": next_q.json, "user": user.uid})
