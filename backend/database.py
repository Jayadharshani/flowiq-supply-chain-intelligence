from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
 
# ==========================================================
# DATABASE CONNECTION
# ==========================================================
# This ONE line is the only thing that changes when you move to
# Render's PostgreSQL later:
#
#   Local (now):      "sqlite:///./flowiq.db"
#   Render (later):   "postgresql://user:password@host:port/dbname"
#                      (Render gives you this exact string when you
#                       create a PostgreSQL instance there)
#
# Everything else in this file, models.py, and app.py stays IDENTICAL
# regardless of which database is behind it - that's the whole point
# of using SQLAlchemy instead of writing raw SQL for one specific DB.
 
DATABASE_URL = "sqlite:///./flowiq.db"
 
# connect_args is only needed for SQLite (it's a quirk of how SQLite
# handles multiple requests) - remove this line if/when you switch
# to PostgreSQL, it's not needed there.
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
 
# A "session" is a temporary conversation with the database - you
# open one, do some reads/writes, then close it. SessionLocal is a
# factory that creates these sessions on demand.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
 
# Base is a parent class that all our table-definition classes
# (in models.py) will inherit from - this is how SQLAlchemy knows
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
 