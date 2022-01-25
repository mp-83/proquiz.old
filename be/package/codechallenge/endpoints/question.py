import logging

from codechallenge.entities import Question
from codechallenge.security import login_required
from pyramid.response import Response
from pyramid.view import view_config, view_defaults

logger = logging.getLogger(__name__)


@view_defaults(request_method="GET")
class QuestionEndPoints:
    def __init__(self, request):
        self.request = request

    @view_config(
        route_name="question", renderer="codechallenge:templates/question_page.jinja2"
    )
    def question(self):
        index = self.request.params.get("index", 0)
        result = Question().at_position(int(index))
        return result.json if result else {}

    @login_required
    @view_config(
        route_name="new_question",
        renderer="codechallenge:templates/new_question.jinja2",
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
        renderer="codechallenge:templates/new_question.jinja2",
        request_method="POST",
    )
    def edit_question(self):
        data = getattr(self.request, "json", None)
        # TODO to complete

        if not data:
            return {}
        return {}
