import logging

from codechallenge.entities import Game, Match, Question
from codechallenge.security import login_required
from pyramid.response import Response
from pyramid.view import view_config

logger = logging.getLogger(__name__)


class MatchEndPoints:
    def __init__(self, request):
        self.request = request

    @login_required
    @view_config(
        route_name="match",
        request_method="GET",
    )
    def get_match(self):
        return Response(json={"match": {}})

    @login_required
    @view_config(
        route_name="match",
        renderer="codechallenge:templates/new_question.jinja2",  # TODO: to fix
        request_method="POST",
    )
    def create_match(self):
        data = self.request.json
        new_match = Match(name=data.get("name")).create()
        new_game = Game(match_uid=new_match.uid).create()
        for position, question in enumerate(data.get("questions", [])):
            new = Question(
                game_uid=new_game.uid, text=question["text"], position=position
            )
            new.create_with_answers(question.get("answers"))
        return Response(json={"match": new_match.json})
