from pydantic import BaseModel
from typing import List, Dict, Optional

class VehicleSpec(BaseModel):
    id: Optional[str]
    automaker: str
    model: str
    version: str
    year: str
    result: Dict[str, str]
    equipments: List[str]

    class Config:
        orm_mode = True