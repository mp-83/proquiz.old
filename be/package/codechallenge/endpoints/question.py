import logging

from codechallenge.entities import Question, Questions
from codechallenge.security import login_required
from pyramid.response import Response
from pyramid.view import view_config, view_defaults

logger = logging.getLogger(__name__)


@view_defaults(request_method="GET")
class QuestionEndPoints:
    def __init__(self, request):
        self.request = request

    @view_config(route_name="question")
    def question(self):
        uid = self.request.matchdict.get("uid")
        question = Questions.get(uid)
        if not question:
            return Response(status=404)

        return Response(json=question.json)

    @login_required
    @view_config(
        route_name="new_question",
        request_method="POST",
    )
    def new_question(self):
        data = getattr(self.request, "json", None)
        if not data:
            return {}
        new_question = Question(**data).save()
        return Response(json=new_question.json)

    @login_required
    @view_config(
        route_name="edit_question",
        request_method="PATCH",
    )
    def edit_question(self):
        uid = self.request.matchdict.get("uid")
        data = getattr(self.request, "json", None)

        question = Questions.get(uid)
        if not question:
            return Response(status=404)

        question.update(**data)
        return Response(json=question.json)
