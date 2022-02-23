import logging

from codechallenge.entities import Matches, User, Users
from codechallenge.exceptions import NotFoundObjectError, ValidateError
from codechallenge.play.single_player import PlayerStatus, SinglePlayer
from codechallenge.validation.logical import ValidatePlayNext
from pyramid.response import Response
from pyramid.view import view_config

logger = logging.getLogger(__name__)


class PlayEndPoints:
    def __init__(self, request):
        self.request = request

    @view_config(route_name="land", request_method="POST")
    def land(self):
        user = None
        data = getattr(self.request, "json", None)
        match = Matches.get(data.get("match"))
        if not match:
            return Response(status=404)

        if match.is_restricted:
            user = Users.get_private_user(mhash=data.get("uhash"))

        if not user:
            user = User(private=match.is_restricted).save()

        return Response(json={"match": match.uid, "user": user.uid})

    @view_config(route_name="start", request_method="POST")
    def start(self):
        data = getattr(self.request, "json", None)
        match = Matches.get(data.get("match"))
        user = Users.get(uid=data.get("user"))
        if not match:
            return Response(status=404)

        if not match.is_valid:
            return Response(status=400, json={"error": "Invalid match"})

        if not match.left_attempts(user):
            return Response(status=400, json={"error": "Invalid match"})

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
        try:
            data = ValidatePlayNext(**user_input).is_valid()
        except (NotFoundObjectError, ValidateError) as e:
            if isinstance(e, NotFoundObjectError):
                return Response(status=404)
            return Response(status=400, json=e)

        match = data.get("match")
        user = data.get("user")
        answer = data.get("answer")

        status = PlayerStatus(user, match)
        player = SinglePlayer(status, user, match)
        next_q = player.react(answer)

        return Response(json={"question": next_q.json, "user": user.uid})
