from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship
import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    generate_quota = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.now)

    transactions = relationship("Transaction", back_populates="user")

class IPLog(Base):
    __tablename__ = "ip_logs"

    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String, index=True)
    date = Column(Date, index=True, default=datetime.date.today)
    usage_count = Column(Integer, default=0)

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    amount_rmb = Column(Integer) # e.g. 5 
    quota_added = Column(Integer) # e.g. 10
    created_at = Column(DateTime, default=datetime.datetime.now)

    user = relationship("User", back_populates="transactions")
