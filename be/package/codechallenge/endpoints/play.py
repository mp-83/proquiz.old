import logging

# TODO remove the Match model when the validation is implemented
from codechallenge.entities import Matches
from codechallenge.play.single_player import SinglePlayer
from pyramid.response import Response
from pyramid.view import view_config

logger = logging.getLogger(__name__)


class PlayEndPoints:
    def __init__(self, request):
        self.request = request

    @view_config(route_name="start", request_method="POST")
    def start(self):
        data = getattr(self.request, "json", None)
        # TODO the match value should be returned by the validation
        match = Matches.get(data.get("match"))
        user = self.request.identity
        player = SinglePlayer(user, match)
        current_question = player.start()
        match_data = {
            "question": current_question.text,
            "answers": [a.text for a in current_question.answers],
        }
        return Response(json=match_data)
