from dataclasses import dataclass
from typing import Optional


@dataclass
class Component:
    name: str
    version: str
    package_type: str
    namespace: Optional[str] = None
    purl: Optional[str] = None
    group_id: Optional[str] = None
    artifact_id: Optional[str] = None