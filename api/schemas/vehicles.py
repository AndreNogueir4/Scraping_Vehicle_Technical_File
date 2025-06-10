from pydantic import BaseModel
from typing import List, Dict

class VehicleBase(BaseModel):
    sheet_code: str
    automaker: str
    model: str
    version: str
    year: str

class Vehicle(VehicleBase):
    result: Dict
    equipments: List[str]

    class Config:
        from_attributes = True

class VehicleList(BaseModel):
    sheet_code: str
    automaker: str
    model: str
    version: str
    year: str