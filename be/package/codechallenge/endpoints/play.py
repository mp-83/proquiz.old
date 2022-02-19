import logging

from codechallenge.entities import Matches, User, Users
from codechallenge.play.single_player import PlayerStatus, SinglePlayer
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
            user = User(private=match.is_restricted).create()

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
        data = getattr(self.request, "json", None)
        match = Matches.get(data.get("match"))
        user = Users.get(uid=data.get("user"))

        if not match:
            return Response(status=404)

        status = PlayerStatus(user, match)
        SinglePlayer(status, user, match)

        # TODO: to fix

        # if answer is among the one of this question's answer
        # if no same reaction has been recorded already
        return Response(json={})
