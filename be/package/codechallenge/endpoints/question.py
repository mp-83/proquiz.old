import logging

from codechallenge.entities import Question
from codechallenge.exceptions import NotFoundObjectError
from codechallenge.security import login_required
from codechallenge.utils import view_decorator
from codechallenge.validation.logical import RetrieveObject
from codechallenge.validation.syntax import create_question_schema, edit_question_schema
from pyramid.response import Response

logger = logging.getLogger(__name__)


class QuestionEndPoints:
    def __init__(self, request):
        self.request = request

    @login_required
    @view_decorator(route_name="get_question", request_method="GET")
    def get_question(self):
        uid = self.request.matchdict.get("uid")
        try:
            question = RetrieveObject(uid=uid, otype="question").get()
        except NotFoundObjectError:
            return Response(status=404)

        return Response(json=question.json)

    @login_required
    @view_decorator(
        route_name="new_question",
        request_method="POST",
        syntax=create_question_schema,
        data_attr="json",
    )
    def new_question(self, user_input):
        new_question = Question(**user_input).save()
        return Response(json=new_question.json)

    @login_required
    @view_decorator(
        route_name="edit_question",
        request_method="PATCH",
        syntax=edit_question_schema,
        data_attr="json",
    )
    def edit_question(self, user_input):
        uid = self.request.matchdict.get("uid")
        try:
            question = RetrieveObject(uid=uid, otype="question").get()
        except NotFoundObjectError:
            return Response(status=404)

        question.update(**user_input)
        return Response(json=question.json)
