import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
 
# ==========================================================
# DATABASE CONNECTION
# ==========================================================
# Reads DATABASE_URL from an environment variable if one is set
# (this is how Render provides the PostgreSQL connection string in
# production) - and falls back to local SQLite if not (this is what
# happens when you run `python app.py` on your own laptop, since no
# such environment variable exists there).
#
# This means the SAME code works in both places without editing it -
# only the environment differs, not the source code.
 
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./flowiq.db")
 
# connect_args is only needed for SQLite (it's a quirk of how SQLite
# handles multiple requests) - PostgreSQL doesn't need it, so we only
# pass it when we're actually using SQLite.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
 
engine = create_engine(DATABASE_URL, connect_args=connect_args)
 
# A "session" is a temporary conversation with the database - you
# open one, do some reads/writes, then close it. SessionLocal is a
# factory that creates these sessions on demand.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
 
# Base is a parent class that all our table-definition classes
# (in DB_models.py) will inherit from - this is how SQLAlchemy knows
# which Python classes represent database tables.
Base = declarative_base()
 
 
def get_db():
    """
    Used by FastAPI to hand each request its own database session,
    and guarantee it gets closed afterward even if an error occurs.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
 