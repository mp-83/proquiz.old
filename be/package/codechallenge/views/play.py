import logging

# TODO remove the Match model when the validation is implemented
from codechallenge.models import Matches
from codechallenge.play.single_player import SinglePlayer
from codechallenge.security import login_required
from pyramid.response import Response
from pyramid.view import view_config, view_defaults

logger = logging.getLogger(__name__)


@view_defaults(request_method="GET")
class PlayViews:
    def __init__(self, request):
        self.request = request

    @login_required
    @view_config(
        route_name="start", renderer="codechallenge:templates/play_page.jinja2"
    )
    def start(self):
        data = getattr(self.request, "json", None)
        # TODO the match value should be returned by the validation
        match = Matches.with_name(data["name"])
        user = self.request.identity
        player = SinglePlayer(user, match)
        current_question = player.start()
        match_data = {
            "question": current_question.text,
            "answers": [a.text for a in current_question.answers],
        }
        return Response(json=match_data)
