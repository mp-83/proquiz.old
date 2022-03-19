import logging

from codechallenge.entities import Game, Match, Matches, Question
from codechallenge.exceptions import NotFoundObjectError, ValidateError
from codechallenge.security import login_required
from codechallenge.utils import view_decorator
from codechallenge.validation.logical import RetrieveObject, ValidateEditMatch
from codechallenge.validation.syntax import create_match_schema, edit_match_schema
from pyramid.response import Response

logger = logging.getLogger(__name__)


class MatchEndPoints:
    def __init__(self, request):
        self.request = request

    @login_required
    @view_decorator(
        route_name="list_matches",
        request_method="GET",
    )
    def list_matches(self):
        _ = self.request.params
        all_matches = Matches.all_matches(**{})
        return Response(json={"matches": [m.json for m in all_matches]})

    @login_required
    @view_decorator(
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
    @view_decorator(
        route_name="new_match",
        request_method="POST",
        syntax=create_match_schema,
        data_attr="json",
    )
    def create_match(self, user_input):
        questions = user_input.pop("questions", [])
        new_match = Match(**user_input).save()
        new_game = Game(match_uid=new_match.uid).save()
        for position, question in enumerate(questions):
            new = Question(
                game_uid=new_game.uid, text=question["text"], position=position
            )
            new.create_with_answers(question.get("answers"))
        return Response(json={"match": new_match.json})

    @login_required
    @view_decorator(
        route_name="edit_match",
        request_method="PATCH",
        syntax=edit_match_schema,
        data_attr="json",
    )
    def edit_match(self, user_input):
        uid = self.request.matchdict.get("uid")

        try:
            match = ValidateEditMatch(uid).is_valid()
        except (NotFoundObjectError, ValidateError) as e:
            if isinstance(e, NotFoundObjectError):
                return Response(status=404)
            return Response(status=400, json={"error": e.message})

        match.update(**user_input)
        return Response(json={"match": match.json})
