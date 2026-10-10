from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


def create_session_factory(database_url: str) -> sessionmaker[Session]:
    """One engine and its connection pool per process; sessions borrow from it."""
    # pool_pre_ping replaces a connection Postgres dropped instead of failing on it.
    engine = create_engine(database_url, pool_pre_ping=True)
    # Domain objects are built inside the session; nothing is reread after commit.
    return sessionmaker(engine, expire_on_commit=False)
