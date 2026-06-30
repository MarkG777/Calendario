from __future__ import annotations

from sqlalchemy import Engine, create_engine, inspect, text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from data.models import Base


def create_engine_for(db_path: str) -> Engine:
    if db_path == ":memory:":
        return create_engine(
            "sqlite://",
            poolclass=StaticPool,
            connect_args={"check_same_thread": False},
        )
    return create_engine(f"sqlite:///{db_path}")


def _run_migrations(engine: Engine) -> None:
    """Add columns that were introduced after the initial schema."""
    inspector = inspect(engine)

    migrations: list[tuple[str, str, str, str]] = [
        ("borrowers", "latitude", "FLOAT", "NULL"),
        ("borrowers", "longitude", "FLOAT", "NULL"),
    ]

    for table, column, col_type, col_default in migrations:
        if table not in inspector.get_table_names():
            continue
        existing = {col["name"] for col in inspector.get_columns(table)}
        if column not in existing:
            with engine.begin() as conn:
                conn.execute(
                    text(
                        f"ALTER TABLE {table} "
                        f"ADD COLUMN {column} {col_type} "
                        f"DEFAULT {col_default}"
                    )
                )


def init_db(engine: Engine) -> None:
    Base.metadata.create_all(engine)
    _run_migrations(engine)


def session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine)
