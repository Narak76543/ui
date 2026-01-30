from sqlalchemy import Column, Integer, String
from core.db import Base

class Village(Base):
    __tablename__ = "villages"

    id                 = Column(Integer, primary_key=True, index=True)
    unique_id          = Column(String, unique=True, index=True)
    name_khmer         = Column(String)
    bot_token          = Column(String)
    commune_chat_id    = Column(String)
    district_chat_id   = Column(String)
    province_chat_id   = Column(String)
    commune_bot_token  = Column(String)
    district_bot_token = Column(String)
    