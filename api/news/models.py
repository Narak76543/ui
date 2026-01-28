from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from core.db import Base

class News(Base):
    __tablename__ = "news"

    id           = Column(Integer, primary_key=True, index=True)
    title        = Column(String(255), nullable=False)
    content      = Column(Text, nullable=False)
    village_name = Column(String(100))
    commune_name = Column(String(100))
    created_at   = Column(DateTime(timezone=True), server_default=func.now())