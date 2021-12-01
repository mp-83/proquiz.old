import logging

from codechallenge.models.question import Question
from pyramid.view import view_config, view_defaults

logger = logging.getLogger(__name__)


@view_defaults(request_method="GET")
class CodeChallengeViews:
    def __init__(self, request):
        self.request = request

    @view_config(route_name="start", renderer="start_page.jinja2")
    def start(self):
        logger.info("Start page")
        return {}

    @view_config(route_name="question", renderer="question_page.jinja2")
    def question(self):
        index = self.request.params.get("index", 0)
        result = Question().at_position(int(index))
        return result.json
