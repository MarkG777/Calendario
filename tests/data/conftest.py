import pytest

from data.database import create_engine_for, init_db, session_factory


@pytest.fixture
def session():
    engine = create_engine_for(":memory:")
    init_db(engine)
    factory = session_factory(engine)
    db_session = factory()
    try:
        yield db_session
    finally:
        db_session.close()
