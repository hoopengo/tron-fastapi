from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.database import Base


class AddressQuery(Base):
    __tablename__ = "address_queries"

    id = Column(Integer, primary_key=True, index=True)
    address = Column(String, index=True)
    balance_trx = Column(Float)
    bandwidth = Column(Integer)
    energy = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
