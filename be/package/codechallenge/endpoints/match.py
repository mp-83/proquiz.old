import logging

from cerberus import Validator
from codechallenge.entities import Game, Match, Question
from codechallenge.exceptions import NotFoundObjectError, ValidateError
from codechallenge.security import login_required
from codechallenge.validation.logical import RetrieveObject, ValidateEditMatch
from codechallenge.validation.syntax import create_match_schema, edit_match_schema
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
        try:
            match = RetrieveObject(uid=uid, otype="match").get()
        except NotFoundObjectError:
            return Response(status=404)

        return Response(json={"match": match.json})

    @login_required
    @view_config(
        route_name="new_match",
        # renderer="codechallenge:templates/new_question.jinja2" TODO: to fix
        request_method="POST",
    )
    def create_match(self):
        user_data = getattr(self.request, "json", None)
        v = Validator(create_match_schema)
        if not v.validate(user_data):
            return Response(status=400, json=v.errors)

        new_match = Match(name=user_data.get("name")).save()
        new_game = Game(match_uid=new_match.uid).save()
        for position, question in enumerate(user_data.get("questions", [])):
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
        user_data = getattr(self.request, "json", None)
        v = Validator(edit_match_schema)
        if not v.validate(user_data):
            return Response(status=400, json=v.errors)

        try:
            match = ValidateEditMatch(uid).is_valid()
        except (NotFoundObjectError, ValidateError) as e:
            if isinstance(e, NotFoundObjectError):
                return Response(status=404)
            return Response(status=400, json={"error": e.message})

        match.update(**v.document)
        return Response(json={"match": match.json})
