import os
import pytest
import uuid
from sqlalchemy import create_engine
from contextlib import contextmanager

from sqlalchemy_utils import create_database, drop_database
from yarl import URL

from test_stairway import alembic_config_from_url
from settings import get_settings

@contextmanager
def tmp_database(db_url: URL, suffix: str = '', **kwargs):
    # # Creating and dropping new db — useful for local testing
    # tmp_db_name = '.'.join([uuid.uuid4().hex, 'test', suffix])
    # tmp_db_url = str(db_url.with_path(tmp_db_name))
    # create_database(tmp_db_url, **kwargs)

    # try:
    #     yield tmp_db_url
    # finally:
    #     drop_database(tmp_db_url)

    # Using test db
    yield get_settings().test_db_url


@pytest.fixture(scope='session')
def pg_url():
    """
    Provides base PostgreSQL URL for creating temporary databases.
    """
    return URL(os.getenv('CI_STAFF_PG_URL', get_settings().test_db_url))


@pytest.fixture
def postgres(pg_url):
    """
    Creates empty temporary database.
    """
    with tmp_database(pg_url, 'pytest') as tmp_url:
        yield tmp_url


@pytest.fixture()
def postgres_engine(postgres):
    """
    SQLAlchemy engine, bound to temporary database.
    """
    engine = create_engine(postgres, echo=True)
    try:
        yield engine
    finally:
        engine.dispose()


@pytest.fixture()
def alembic_config(postgres):
    """
    Alembic configuration object, bound to temporary database.
    """
    return alembic_config_from_url(postgres)
