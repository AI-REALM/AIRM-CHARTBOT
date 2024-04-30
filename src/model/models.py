from sqlalchemy import Column, BigInteger, String, Boolean, Date, Float
from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Note that you will also need to handle the Base metadata creation and
# potentially the database session creation somewhere in your code. This is
# typically handled in a separate file such as database.py, which will contain
# your SQLAlchemy engine, session, and Base metadata configuration.

class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True)
    premium = Column(Boolean, default=False, nullable=False)
    premium_date = Column(Date, nullable=True)
    indicators = Column(String, nullable=True)
    interval = Column(String, nullable=False)
    style = Column(String, nullable=False)
    timezone = Column(String, nullable=False)
    chain = Column(String, nullable=False)
    status = Column(String, nullable=False)


class Notify(Base):
    __tablename__ = "notify"

    notify_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    chat_id = Column(BigInteger, nullable=False)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    crypto_type = Column(String, nullable=False)
    name = Column(String, nullable=False)
    symbol = Column(String, nullable=False)
    chain = Column(String, nullable=False)
    platform = Column(String, nullable=False)
    condition = Column(String, nullable=False)
    con_type = Column(String, nullable=False)
    value = Column(Float, nullable=True)
    notify_method = Column(String, nullable=True)