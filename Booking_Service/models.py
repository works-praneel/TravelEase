from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from database import Base

class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True)
    destination = Column(String(100), nullable=False)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    user_email = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # Relationship with recommendations
    recommendations = relationship("Recommendation", back_populates="trip")

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True)
    trip_id = Column(Integer, ForeignKey("trips.id"), nullable=False)
    suggestion_type = Column(String(50))  # 'hotel', 'cab', etc.
    name = Column(String(100))
    description = Column(String(255))
    price = Column(Float)
    created_at = Column(DateTime, server_default=func.now())

    trip = relationship("Trip", back_populates="recommendations")
