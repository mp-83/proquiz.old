import os

import alembic
import alembic.command
import alembic.config
import pytest
import transaction
from codechallenge.app import StoreConfig, main
from codechallenge.models import Question
from codechallenge.models.meta import (
    Base,
    get_engine,
    get_session_factory,
    get_tm_session,
)
from pyramid.config import Configurator
from pyramid.paster import get_appsettings


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
def tm():
    tm = transaction.TransactionManager(explicit=True)
    tm.begin()
    tm.doom()

    yield tm

    tm.abort()


@pytest.fixture
def _sessionTestDB(app, tm):
    session_factory = app.registry["dbsession_factory"]
    return get_tm_session(session_factory, tm)


@pytest.fixture
def sessionTestDB(dbengine):
    session_factory = get_session_factory(dbengine)
    sc = StoreConfig()
    configurator = Configurator()
    configurator.registry["dbsession_factory"] = session_factory
    sc.config = configurator
    yield sc.session


@pytest.fixture
def fillTestingDB(dbengine, sessionTestDB):
    db_session = sessionTestDB
    with transaction.manager:
        db_session.add_all(
            [
                Question(text="q1.text", code="q1.code", position=1),
                Question(text="q2.text", code="q2.code", position=2),
                Question(text="q3.text", code="q3.code", position=3),
            ]
        )
        db_session.commit()

    yield

    # Base.metadata.drop_all(engine_factory)
