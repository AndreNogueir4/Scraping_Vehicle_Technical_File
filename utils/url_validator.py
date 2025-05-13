import re
from urllib.parse import urlparse


def sanitize_url(url: str) -> str:
    url = re.sub(r'[\s\u200b\u200e\u200f\u00a0]+', '', url.strip())
    return url


def is_valid_url(url: str) -> bool:
    parsed = urlparse(url)
    return bool(parsed.scheme and parsed.netloc)