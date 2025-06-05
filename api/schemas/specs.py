from pydantic import BaseModel
from typing import List, Dict

class VehicleSpec(BaseModel):
    id: str
    automaker: str
    model: str
    version: str
    year: str
    result: Dict[str, str]
    equipments: List[str]