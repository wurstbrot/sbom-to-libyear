from dataclasses import dataclass
from typing import Optional, Dict


@dataclass
class RepositoryConfig:
    name: str
    url: str
    search_url: Optional[str] = None
    enabled: bool = True
    priority: int = 1
    auth: Optional[Dict[str, str]] = None