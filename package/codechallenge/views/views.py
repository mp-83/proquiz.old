import logging

from codechallenge.models.question import Question
from pyramid.view import view_config, view_defaults

logger = logging.getLogger(__name__)


@view_defaults(request_method="GET")
class CodeChallengeViews:
    def __init__(self, request):
        self.request = request

    @view_config(
        route_name="start", renderer="codechallenge:templates/start_page.jinja2"
    )
    def start(self):
        logger.info("Start page")
        return {}

    @view_config(
        route_name="question", renderer="codechallenge:templates/question_page.jinja2"
    )
    def question(self):
        index = self.request.params.get("index", 0)
        result = Question().at_position(int(index))
        return result.json if result else {}

    @view_config(
        route_name="new_question",
        renderer="codechallenge:templates/new_question.jinja2",
        request_method="POST",
    )
    def new_question(self):
        data = self.request.params.get("data", {})
        if not data:
            return {}
        new_question = Question(**data).save()
        return new_question.json