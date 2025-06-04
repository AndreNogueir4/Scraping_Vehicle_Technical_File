from dataclasses import dataclass
from typing import Dict, List

@dataclass
class Automaker:
    name: str
    url_slug: str
    source: str
    url: str

@dataclass
class Model:
    name: str
    url_slug: str
    automaker: str
    source: str
    url: str

@dataclass
class VersionYear:
    name: str
    year: str
    url: str
    model: str
    automaker: str
    source: str

@dataclass
class TechnicalSheet:
    specifications: Dict[str, str]
    equipment: List[str]
    source_url: str
    automaker: str
    model: str
    version: str
    source: str