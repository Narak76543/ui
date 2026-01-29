from pydantic import BaseModel
from typing import Optional

class VillageBase(BaseModel):
    unique_id       : str
    name_khmer      : str
    bot_token       : str
    commune_chat_id : str
    district_chat_id: str
    province_chat_id: str

class VillageCreate(VillageBase):
    pass

class VillageRead(VillageBase):
    id: int

    class Config:
        from_attributes = True