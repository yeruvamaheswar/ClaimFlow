import pytest
from sqlalchemy import create_engine, text

from app.database import SCHEMA_VERSION, Base, check_schema_version


def make_engine(tmp_path):
    return create_engine(f"sqlite:///{tmp_path / 'schema.db'}")


def user_version(engine):
    with engine.connect() as conn:
        return conn.execute(text("PRAGMA user_version")).scalar_one()


def test_mismatched_version_raises_with_delete_hint(tmp_path):
    engine = make_engine(tmp_path)
    with engine.begin() as conn:
        conn.execute(text("PRAGMA user_version = 99"))
    with pytest.raises(RuntimeError) as error:
        check_schema_version(engine)
    message = str(error.value)
    assert "Delete the DB file" in message
    assert "schema.db" in message
    assert user_version(engine) == 99
    engine.dispose()


def test_unstamped_db_with_tables_is_stamped(tmp_path):
    engine = make_engine(tmp_path)
    Base.metadata.create_all(engine)
    assert user_version(engine) == 0
    check_schema_version(engine)
    assert user_version(engine) == SCHEMA_VERSION
    check_schema_version(engine)  # matching version passes
    engine.dispose()
