from dataclasses import dataclass

@dataclass
class Automaker:
    name: str
    url_slug: str
    source: str
    url: str