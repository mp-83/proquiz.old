def default_routes(config):
    config.add_route("home", "/")
    config.add_route("login", "/login")
    config.add_route("logout", "/logout")
    config.add_route("question", "/question")
    config.add_route("new_question", "/new_question")
    config.add_route("edit_question", "/edit_question/{uid}")
    config.add_route("match", "/match")


def play_routes(config):
    config.add_route("start", "/start")


def includeme(config):
    config.include(default_routes)
    config.include(play_routes, route_prefix="/play")

    config.add_static_view(name="static", path="codechallenge:static")

    config.scan("codechallenge.endpoints.ep_match")
    config.scan("codechallenge.endpoints.ep_play")
