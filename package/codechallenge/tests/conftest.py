import os

import alembic
import alembic.command
import alembic.config
import pytest
import transaction
import webtest
from codechallenge.app import main
from codechallenge.models import Question
from codechallenge.models.meta import Base, get_engine, get_tm_session
from codechallenge.security import SecurityPolicy
from pyramid.paster import get_appsettings
from pyramid.testing import DummyRequest, testConfig
from webob.cookies import Cookie


class TestApp(webtest.TestApp):
    def get_cookie(self, name, default=None):
        # webtest currently doesn't expose the unescaped cookie values
        # so we're using webob to parse them for us
        # see https://github.com/Pylons/webtest/issues/171
        cookie = Cookie(
            " ".join(
                "%s=%s" % (c.name, c.value) for c in self.cookiejar if c.name == name
            )
        )
        return next(
            (m.value.decode("latin-1") for m in cookie.values()),
            default,
        )

    def get_csrf_token(self):
        """
        Convenience method to get the current CSRF token.

        This value must be passed to POST/PUT/DELETE requests in either the
        "X-CSRF-Token" header or the "csrf_token" form value.

        testapp.post(..., headers={'X-CSRF-Token': testapp.get_csrf_token()})

        or

        testapp.post(..., {'csrf_token': testapp.get_csrf_token()})

        """
        return self.get_cookie("csrf_token")

    def login(self, params, status=303, **kw):
        """Convenience method to login the client."""
        body = {"csrf_token": self.get_csrf_token()}
        body.update(params)
        return self.post("/login", body, **kw)


def pytest_addoption(parser):
    parser.addoption("--ini", action="store", metavar="INI_FILE")


@pytest.fixture(scope="session")
def ini_file(request):
    # potentially grab this path from a pytest option
    return os.path.abspath("pytest.ini")


@pytest.fixture(scope="session")
def alembic_ini_file(request):
    return os.path.abspath("alembic.ini")


@pytest.fixture(scope="session")
def app_settings(ini_file):
    _sett = get_appsettings(ini_file)
    yield _sett


@pytest.fixture
def dbengine(app_settings, ini_file, alembic_ini_file):
    engine = get_engine(app_settings)

    alembic_cfg = alembic.config.Config(alembic_ini_file)
    Base.metadata.drop_all(bind=engine)
    alembic.command.stamp(alembic_cfg, None, purge=True)

    # run migrations to initialize the database
    # depending on how we want to initialize the database from scratch
    # we could alternatively call:
    Base.metadata.create_all(bind=engine)
    # alembic.command.stamp(alembic_cfg, "head")
    # alembic.command.upgrade(alembic_cfg, "head")

    yield engine

    Base.metadata.drop_all(bind=engine)
    # alembic.command.stamp(alembic_cfg, None, purge=True)


@pytest.fixture
def app(app_settings, dbengine):
    return main({}, dbengine=dbengine, **app_settings)


@pytest.fixture
def testapp(app, tm, dbsession):
    # override request.dbsession and request.tm with our own
    # externally-controlled values that are shared across requests but aborted
    # at the end
    _testapp = TestApp(
        app,
        extra_environ={
            "HTTP_HOST": "example.com",
            "tm.active": True,
            "tm.manager": tm,
            "app.dbsession": dbsession,
        },
    )

    # initialize a csrf token instead of running an initial request to get one
    # from the actual app - this only works using the CookieCSRFStoragePolicy
    _testapp.set_cookie("csrf_token", "dummy_csrf_token")

    return _testapp


@pytest.fixture
def tm():
    tm = transaction.TransactionManager(explicit=True)
    tm.begin()
    tm.doom()

    yield tm

    tm.abort()


@pytest.fixture
def dbsession(app, tm):
    session_factory = app.registry["dbsession_factory"]
    return get_tm_session(session_factory, tm)


@pytest.fixture
def fillTestingDB(app):
    tm = transaction.TransactionManager(explicit=True)
    dbsession = get_tm_session(app.registry["dbsession_factory"], tm)
    with tm:
        dbsession.add_all(
            [
                Question(text="q1.text", code="q1.code", position=1),
                Question(text="q2.text", code="q2.code", position=2),
                Question(text="q3.text", code="q3.code", position=3),
            ]
        )

    yield


@pytest.fixture
def dummy_request(tm, dbsession):
    """
    A lightweight dummy request.

    This request is ultra-lightweight and should be used only when the request
    itself is not a large focus in the call-stack.  It is much easier to mock
    and control side-effects using this object, however:

    - It does not have request extensions applied.
    - Threadlocals are not properly pushed.

    """
    request = DummyRequest()
    request.domain = "codechallenge.project"
    request.host = "codechallenge.project"
    request.dbsession = dbsession
    request.tm = tm

    return request


@pytest.fixture
def simple_config(dummy_request):
    """
    A dummy :class:`pyramid.config.Configurator` object.  This allows for
    mock configuration, including configuration for ``dummy_request``, as well
    as pushing the appropriate threadlocals.

    """
    with testConfig(request=dummy_request) as config:
        config.add_route("login", "/login")
        config.add_route("logout", "/logout")
        config.add_route("start", "/start")
        config.add_route("new_question", "/new_question")
        config.add_route("edit_question", "/edit_question/{uid}")
        yield config


@pytest.fixture
def functional_config(dummy_request, app_settings):
    with testConfig(request=dummy_request) as config:
        config.add_route("login", "/login")
        config.add_route("logout", "/logout")
        config.add_route("start", "/start")
        config.add_route("new_question", "/new_question")
        config.add_route("edit_question", "/edit_question/{uid}")

        config.set_security_policy(SecurityPolicy(app_settings["auth.secret"]))
        yield config
