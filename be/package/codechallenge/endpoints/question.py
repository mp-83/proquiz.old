import logging

from cerberus import Validator
from codechallenge.entities import Question
from codechallenge.exceptions import NotFoundObjectError
from codechallenge.security import login_required
from codechallenge.validation.logical import RetrieveObject
from codechallenge.validation.syntax import create_question_schema, edit_question_schema
from pyramid.response import Response
from pyramid.view import view_config, view_defaults

logger = logging.getLogger(__name__)


@view_defaults(request_method="GET")
class QuestionEndPoints:
    def __init__(self, request):
        self.request = request

    @login_required
    @view_config(route_name="get_question")
    def get_question(self):
        uid = self.request.matchdict.get("uid")
        try:
            question = RetrieveObject(uid=uid, otype="question").get()
        except NotFoundObjectError:
            return Response(status=404)

        return Response(json=question.json)

    @login_required
    @view_config(
        route_name="new_question",
        request_method="POST",
    )
    def new_question(self):
        user_data = getattr(self.request, "json", None)
        v = Validator(create_question_schema)
        if not v.validate(user_data):
            return Response(status=400, json=v.errors)

        new_question = Question(**v.document).save()
        return Response(json=new_question.json)

    @login_required
    @view_config(
        route_name="edit_question",
        request_method="PATCH",
    )
    def edit_question(self):
        uid = self.request.matchdict.get("uid")
        user_data = getattr(self.request, "json", None)
        v = Validator(edit_question_schema)
        if not v.validate(user_data):
            return Response(status=400, json=v.errors)

        try:
            question = RetrieveObject(uid=uid, otype="question").get()
        except NotFoundObjectError:
            return Response(status=404)

        question.update(**v.document)
        return Response(json=question.json)
