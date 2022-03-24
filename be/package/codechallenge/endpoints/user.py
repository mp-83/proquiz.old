import logging

from codechallenge.entities import Users
from codechallenge.security import login_required
from codechallenge.utils import view_decorator
from codechallenge.validation.syntax import player_list_schema
from pyramid.response import Response

logger = logging.getLogger(__name__)


class UserPoints:
    def __init__(self, request):
        self.request = request

    @login_required
    @view_decorator(
        route_name="list_players",
        request_method="GET",
        syntax=player_list_schema,
        data_attr="params",
    )
    def list_players(self, user_input):
        match_uid = user_input["match_uid"]
        all_players = Users.players_of_match(match_uid)
        return Response(json={"players": [u.json for u in all_players]})
