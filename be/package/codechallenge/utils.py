from cerberus import Validator
from codechallenge.exceptions import BaseException
from pyramid.response import Response
from pyramid.view import view_config


class view_decorator(view_config):
    def __call__(self, wrapped):
        settings = self.__dict__.copy()
        syntax_schema = settings.pop("syntax", None)
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
            v = Validator(syntax_schema)
            if not v.validate(user_input):
                return Response(status=400, json=v.errors)

            try:
                return wrapped(*args, v.document)
            except BaseException:
                return Response(status=200)

        return wrapped_f if syntax_schema else wrapped
