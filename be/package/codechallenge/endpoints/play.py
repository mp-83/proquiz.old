import logging

from codechallenge.entities.user import UserFactory
from codechallenge.exceptions import NotFoundObjectError, ValidateError
from codechallenge.play.single_player import PlayerStatus, SinglePlayer
from codechallenge.utils import view_decorator
from codechallenge.validation.logical import (
    ValidatePlayCode,
    ValidatePlayLand,
    ValidatePlayNext,
    ValidatePlaySign,
    ValidatePlayStart,
)
from codechallenge.validation.syntax import (
    code_play_schema,
    land_play_schema,
    next_play_schema,
    sign_play_schema,
    start_play_schema,
)
from pyramid.response import Response

logger = logging.getLogger(__name__)


class PlayEndPoints:
    def __init__(self, request):
        self.request = request

    @view_decorator(
        route_name="land",
        request_method="POST",
        syntax=land_play_schema,
        data_attr="matchdict",
    )
    def land(self, user_input):
        try:
            data = ValidatePlayLand(**user_input).is_valid()
        except (NotFoundObjectError, ValidateError) as e:
            if isinstance(e, NotFoundObjectError):
                return Response(status=404)
            return Response(status=400, json={"error": e.message})

        match = data.get("match")
        return Response(json={"match": match.uid})

    @view_decorator(
        route_name="code",
        request_method="POST",
        syntax=code_play_schema,
        data_attr="json",
    )
    def code(self, user_input):
        try:
            data = ValidatePlayCode(**user_input).is_valid()
        except (NotFoundObjectError, ValidateError) as e:
            if isinstance(e, NotFoundObjectError):
                return Response(status=404)
            return Response(status=400, json={"error": e.message})

        match = data.get("match")
        user = UserFactory(signed=True).fetch()
        return Response(json={"match": match.uid, "user": user.uid})

    @view_decorator(
        route_name="start",
        request_method="POST",
        syntax=start_play_schema,
        data_attr="json",
    )
    def start(self, user_input):
        try:
            data = ValidatePlayStart(**user_input).is_valid()
        except (NotFoundObjectError, ValidateError) as e:
            if isinstance(e, NotFoundObjectError):
                return Response(status=404)
            return Response(status=400, json={"error": e.message})

        match = data.get("match")
        user = data.get("user")
        if not user:
            user = UserFactory(signed=match.is_restricted).fetch()

        status = PlayerStatus(user, match)
        player = SinglePlayer(status, user, match)
        current_question = player.start()
        match_data = {
            "question": current_question.json,
            "answers": [a.json for a in current_question.answers],
            "user": user.uid,
        }
        return Response(json=match_data)

    @view_decorator(
        route_name="next",
        request_method="POST",
        syntax=next_play_schema,
        data_attr="json",
    )
    def next(self, user_input):
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

    @view_decorator(
        route_name="sign",
        request_method="POST",
        syntax=sign_play_schema,
        data_attr="json",
    )
    def sign(self, user_input):
        try:
            data = ValidatePlaySign(**user_input).is_valid()
        except (NotFoundObjectError, ValidateError) as e:
            if isinstance(e, NotFoundObjectError):
                return Response(status=404)
            return Response(status=400, json={"error": e.message})

        user = data.get("user")
        return Response(json={"user": user.uid})
