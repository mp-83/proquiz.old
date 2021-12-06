import os

import alembic
import alembic.command
import alembic.config
import pytest
import transaction
from codechallenge.app import StoreConfig, main
from codechallenge.models import Question
from codechallenge.models.meta import Base, get_engine, get_tm_session
from pyramid.paster import get_appsettings
from webtest import TestApp


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
def dbsession(sessionTestDB):
    yield sessionTestDB


@pytest.fixture
def sessionTestDB(app, tm):
    session_factory = app.registry["dbsession_factory"]
    _ = StoreConfig()
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
