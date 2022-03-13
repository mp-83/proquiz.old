import logging

from cerberus import Validator
from codechallenge.entities.user import UserFactory
from codechallenge.exceptions import NotFoundObjectError, ValidateError
from codechallenge.play.single_player import PlayerStatus, SinglePlayer
from codechallenge.validation.logical import (
    ValidatePlayCode,
    ValidatePlayLand,
    ValidatePlayNext,
    ValidatePlayStart,
)
from codechallenge.validation.syntax import (
    code_play_schema,
    land_play_schema,
    next_play_schema,
    start_play_schema,
)
from pyramid.response import Response
from pyramid.view import view_config

logger = logging.getLogger(__name__)


class syntaxdecorator:
    def __init__(self, **dec_kwargs):
        """
        If there are decorator arguments, the function
        to be decorated is not passed to the constructor!
        """
        print("Inside __init__()")
        self.dec_kwargs = dec_kwargs

    def __call__(self, f):
        """
        If there are decorator arguments, __call__() is only called
        once, as part of the decoration process! You can only give
        it a single argument, which is the function object.
        """

        def wrapped_f(*args, **kwargs):
            request = args[0].request
            schema = self.dec_kwargs.get("schema")
            data_attr = self.dec_kwargs.get("data_attr")
            user_input = getattr(request, data_attr, {})
            v = Validator(schema)
            if not v.validate(user_input):
                return Response(status=400, json=v.errors)

            try:
                return f(*args, v.document)
            except Exception:
                return Response(status=200)

        return wrapped_f


class view_decorator(view_config):
    def __call__(self, wrapped):
        settings = self.__dict__.copy()
        schema = settings.pop("schema", None)
        data_attr = settings.pop("data_attr", None)
        depth = settings.pop("_depth", 0)
        category = settings.pop("_category", "pyramid")

        def callback(context, name, ob):
            config = context.config.with_package(info.module)
            config.add_view(view=ob, **settings)

        info = self.venusian.attach(
            wrapped, callback, category=category, depth=depth + 1
        )

        if info.scope == "class":
            if settings.get("attr") is None:
                settings["attr"] = wrapped.__name__

        def wrapped_f(*args, **kwargs):
            request = args[0].request
            user_input = getattr(request, data_attr, {})
            v = Validator(schema)
            if not v.validate(user_input):
                return Response(status=400, json=v.errors)

            try:
                return wrapped(*args, v.document)
            except Exception:
                return Response(status=200)

        return wrapped_f


class PlayEndPoints:
    def __init__(self, request):
        self.request = request

    @view_decorator(
        route_name="land",
        request_method="POST",
        schema=land_play_schema,
        data_attr="matchdict",
    )
    def land(self, user_input):
        try:
            data = ValidatePlayLand(**user_input).is_valid()
        except (NotFoundObjectError, ValidateError) as e:
            if isinstance(e, NotFoundObjectError):
                return Response(status=404)
            return Response(status=400, json={"error": e.message})

        match = data.get("match")
        user = UserFactory(signed=match.is_restricted).fetch()
        return Response(json={"match": match.uid, "user": user.uid})

    @syntaxdecorator(schema=code_play_schema, data_attr="json")
    @view_config(route_name="code", request_method="POST")
    def code(self, user_input):
        try:
            data = ValidatePlayCode(**user_input).is_valid()
        except (NotFoundObjectError, ValidateError) as e:
            if isinstance(e, NotFoundObjectError):
                return Response(status=404)
            return Response(status=400, json={"error": e.message})

        match = data.get("match")
        user = UserFactory(signed=True).fetch()
        return Response(json={"match": match.uid, "user": user.uid})

    @syntaxdecorator(schema=start_play_schema, data_attr="json")
    @view_config(route_name="start", request_method="POST")
    def start(self, user_input):
        try:
            data = ValidatePlayStart(**user_input).is_valid()
        except (NotFoundObjectError, ValidateError) as e:
            if isinstance(e, NotFoundObjectError):
                return Response(status=404)
            return Response(status=400, json={"error": e.message})

        match = data.get("match")
        user = data.get("user")
        status = PlayerStatus(user, match)
        player = SinglePlayer(status, user, match)
        current_question = player.start()
        match_data = {
            "question": current_question.json,
            "answers": [a.json for a in current_question.answers],
            "user": user.uid,
        }
        return Response(json=match_data)

    @syntaxdecorator(schema=next_play_schema, data_attr="json")
    @view_config(route_name="next", request_method="POST")
    def next(self, user_input):
        try:
            data = ValidatePlayNext(**user_input).is_valid()
        except (NotFoundObjectError, ValidateError) as e:
            if isinstance(e, NotFoundObjectError):
                return Response(status=404)
            return Response(status=400, json={"error": e.message})

        match = data.get("match")
        user = data.get("user")
        answer = data.get("answer")

        status = PlayerStatus(user, match)
        player = SinglePlayer(status, user, match)
        next_q = player.react(answer)

        return Response(json={"question": next_q.json, "user": user.uid})
