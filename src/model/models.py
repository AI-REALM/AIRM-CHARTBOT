from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    indicators = Column(String, nullable=True)
    interval = Column(String, nullable=False)
    style = Column(String, nullable=False)
    timezone = Column(String, nullable=False)
    chain = Column(String, nullable=False)
    status = Column(String, nullable=False)

class Noitfy(Base):
    __tablename__ = "notify"

    notify_id = Column(Integer, primary_key=True, index=True, autoincrement="auto")
    chat_id = Column(Integer, nullable=False)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    crypto_type = Column(String, nullable=False)
    name = Column(String, nullable=False)
    symbol = Column(String, nullable=False)
    chain = Column(String, nullable=False)
    platform = Column(String, nullable=False)
    condition = Column(String, nullable=False)
    value = Column(Integer, nullable=True)
    notify_method = Column(String, nullable=True)