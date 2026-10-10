from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from app.adapters.persistence.sqlalchemy.tables import Base
from sqlalchemy import create_engine


def test_migrations_match_the_table_models(migrated: str) -> None:
    """Fails when tables.py changes without a migration (or the reverse)."""
    engine = create_engine(migrated)
    with engine.connect() as connection:
        diff = compare_metadata(MigrationContext.configure(connection), Base.metadata)
    engine.dispose()
    assert diff == []
