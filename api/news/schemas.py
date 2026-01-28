from pydantic import BaseModel
from datetime import datetime

class NewsCreate(BaseModel):
    title       : str
    content     : str
    village_name: str
    commune_name: str

class NewsResponse(NewsCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True