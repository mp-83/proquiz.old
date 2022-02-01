def default_routes(config):
    config.add_route("home", "/")
    config.add_route("login", "/login")
    config.add_route("logout", "/logout")
    config.add_route("question", "/question")
    config.add_route("new_question", "/question/new")
    config.add_route("edit_question", "/question/edit/{uid}")
    config.add_route("new_match", "/match/new")
    config.add_route("single_match", "/match/{uid}")
    config.add_route("edit_match", "/match/edit/{uid}")


def play_routes(config):
    config.add_route("start", "/start")


def includeme(config):
    config.include(default_routes)
    config.include(play_routes, route_prefix="/play")

    config.add_static_view(name="static", path="codechallenge:static")

    config.scan("codechallenge.endpoints.login")
    config.scan("codechallenge.endpoints.match")
    config.scan("codechallenge.endpoints.question")
    config.scan("codechallenge.endpoints.play")
