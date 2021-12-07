from codechallenge.models import User
from pyramid.authentication import AuthTktCookieHelper
from pyramid.csrf import CookieCSRFStoragePolicy
from pyramid.httpexceptions import HTTPFound
from pyramid.request import RequestLocalCache


class SecurityPolicy:
    def __init__(self, secret):
        self.authtkt = AuthTktCookieHelper(secret)
        self.identity_cache = RequestLocalCache(self.load_identity)

    def load_identity(self, request):
        identity = self.authtkt.identify(request)
        if identity is None:
            return None

        userid = identity["userid"]
        user = request.dbsession.query(User).get(userid)
        return user

    def identity(self, request):
        return self.identity_cache.get_or_create(request)

    def authenticated_userid(self, request):
        user = self.identity(request)
        if user is not None:
            return user.id

    def remember(self, request, userid, **kw):
        return self.authtkt.remember(request, userid, **kw)

    def forget(self, request, **kw):
        return self.authtkt.forget(request, **kw)


def includeme(config):
    settings = config.get_settings()

    config.set_csrf_storage_policy(CookieCSRFStoragePolicy())
    config.set_default_csrf_options(require_csrf=True)

    config.set_security_policy(SecurityPolicy(settings["auth.secret"]))


def login_required(func):
    def function_wrapper(*args, **kwargs):
        view = args[0]
        if view.request.is_authenticated:
            return func(*args, **kwargs)
        login_url = view.request.route_url("login")
        return HTTPFound(login_url)

    return function_wrapper
