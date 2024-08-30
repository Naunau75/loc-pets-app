from sqlalchemy import Column, Integer, Float, String, DateTime
from database import Base


class AnimalPerdu(Base):
    __tablename__ = "animaux_perdus"

    id = Column(Integer, primary_key=True, index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    description = Column(String)
    date_perte = Column(DateTime)
    espece = Column(String)
