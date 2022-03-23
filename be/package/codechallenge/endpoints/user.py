import logging

from codechallenge.entities import Users
from codechallenge.security import login_required
from codechallenge.utils import view_decorator
from pyramid.response import Response

logger = logging.getLogger(__name__)


class UserPoints:
    def __init__(self, request):
        self.request = request

    @login_required
    @view_decorator(
        route_name="list_players",
        request_method="GET",
    )
    def list_players(self):
        # TODO: to fix the filtering parameters
        _ = self.request.params
        all_players = Users.all()
        return Response(json={"players": [u.json for u in all_players]})
