import os
from pyramid.authorization import Allow, Everyone
from sqlalchemy import Column, Integer, String, select, engine_from_config
from sqlalchemy.orm import declarative_base, Session, sessionmaker


cache = {}
Base = declarative_base()


def get_engine(settings, prefix='sqlalchemy.'):
    echo = settings.get('echo', False)
    if not cache.get('engine'):
        cache['engine'] = engine_from_config(settings, prefix, echo=echo)
    return cache['engine']


# def init_session():
#     engine = get_engine()
#     DBSession = Session(engine)
#     return DBSession


def get_session_factory(engine):
    factory = sessionmaker()
    factory.configure(bind=engine)
    return factory


def get_tm_session(session_factory, transaction_manager, request=None):
    """
    Get a ``sqlalchemy.orm.Session`` instance backed by a transaction.
    """
    dbsession = session_factory(info={"request": request})
    zope.sqlalchemy.register(
        dbsession, transaction_manager=transaction_manager
    )
    return dbsession



def includeme(config):
    """
    Initialize the model for a Pyramid app.

    """
    settings = config.get_settings()
    settings['tm.manager_hook'] = 'pyramid_tm.explicit_manager'

    # Use ``pyramid_tm`` to hook the transaction lifecycle to the request.
    # Note: the packages ``pyramid_tm`` and ``transaction`` work together to
    # automatically close the active database session after every request.
    # If your project migrates away from ``pyramid_tm``, you may need to use a
    # Pyramid callback function to close the database session after each
    # request.
    config.include('pyramid_tm')

    # use pyramid_retry to retry a request when transient exceptions occur
    config.include('pyramid_retry')

    # hook to share the dbengine fixture in testing
    dbengine = settings.get('dbengine')
    if not dbengine:
        dbengine = get_engine(settings)

    session_factory = get_session_factory(dbengine)
    config.registry['dbsession_factory'] = session_factory

    # make request.dbsession available for use in Pyramid
    def dbsession(request):
        # hook to share the dbsession fixture in testing
        dbsession = request.environ.get('app.dbsession')
        if dbsession is None:
            # request.tm is the transaction manager used by pyramid_tm
            dbsession = get_tm_session(
                session_factory, request.tm, request=request
            )
        return dbsession

    config.add_request_method(dbsession, reify=True)


class Root:
    __acl__ = [(Allow, Everyone, 'view'),
               (Allow, 'group:editors', 'edit')]

    def __init__(self, request):
        pass
