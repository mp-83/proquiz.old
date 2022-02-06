import logging

from codechallenge.entities import Game, Match, Matches, Question
from codechallenge.security import login_required
from pyramid.response import Response
from pyramid.view import view_config

logger = logging.getLogger(__name__)


class MatchEndPoints:
    def __init__(self, request):
        self.request = request

    @login_required
    @view_config(
        route_name="get_match",
        request_method="GET",
    )
    def get_match(self):
        uid = self.request.matchdict.get("uid")
        match = Matches.get(uid=uid)
        if not match:
            return Response(status=404)
        return Response(json={"match": match.json})

    @login_required
    @view_config(
        route_name="new_match",
        # renderer="codechallenge:templates/new_question.jinja2" TODO: to fix
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

    @login_required
    @view_config(
        route_name="edit_match",
        request_method="PATCH",
    )
    def edit_match(self):
        uid = self.request.matchdict.get("uid")
        match = Matches.get(uid=uid)
        if match.is_started:
            return Response(status=400)

        data = self.request.json
        match.update_attributes(**data)
        match.update_questions(data.get("questions", []))
        return Response(json={"match": match.json})
