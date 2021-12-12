def includeme(config):
    config.add_route("start", "/")
    config.add_route("login", "/login")
    config.add_route("logout", "/logout")
    config.add_route("question", "/question")
    config.add_route("new_question", "/new_question")
    config.add_route("edit_question", "/edit_question/{uid}")
    config.add_route("match", "/match")

    config.add_static_view(name="static", path="codechallenge:static")

    config.scan("codechallenge.views.views")
