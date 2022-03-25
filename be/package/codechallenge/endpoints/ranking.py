from codechallenge.entities import Rankings
from codechallenge.security import login_required
from codechallenge.utils import view_decorator
from codechallenge.validation.syntax import match_rankings_schema
from pyramid.response import Response


class RankingEndPoints:
    def __init__(self, request):
        self.request = request

    @login_required
    @view_decorator(
        route_name="match_rankings",
        request_method="GET",
        syntax=match_rankings_schema,
        data_attr="params",
    )
    def match_rankings(self, user_input):
        match_uid = user_input["match_uid"]
        rankings = Rankings.of_match(match_uid)
        return Response(json={"rankings": [rank.json for rank in rankings]})
