from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from database import Base


class User(Base):
    """
    One row per registered user. Passwords are NEVER stored in plain
    text - only a bcrypt hash of the password is kept (see auth.py).
    Even if this database leaked, the original passwords could not
    be recovered from what's stored here.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class PredictionHistory(Base):
    """
    This class represents a database TABLE. Each attribute below
    becomes a COLUMN. Each time we save a prediction, one ROW gets
    created in this table.

    SQLAlchemy reads this class and generates the actual
    `CREATE TABLE prediction_history (...)` SQL for us - we never
    write raw SQL for this.
    """
    __tablename__ = "prediction_history"

    id = Column(Integer, primary_key=True, index=True)

    # Links this prediction to whichever logged-in user made it.
    # Nullable so old predictions made before login existed still work.
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Key order details worth keeping for later analysis/dashboard
    customer_city = Column(String)
    customer_state = Column(String)
    product_category_name = Column(String)
    price = Column(Float)
    freight_value = Column(Float)
    payment_type = Column(String)

    # The prediction itself
    late_delivery_predicted = Column(Boolean)
    late_probability = Column(Float)
    risk_level = Column(String)

    # Automatically set to the current time when a row is created -
    # we never need to pass this in manually.
    created_at = Column(DateTime(timezone=True), server_default=func.now())