from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String, nullable=True)
    balance = Column(Integer, default=0)
    role = Column(String, default="user")

    purchases = relationship("Purchase", back_populates="user")

class Purchase(Base):
    __tablename__ = "purchases"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    item_name = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    date = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="purchases")
