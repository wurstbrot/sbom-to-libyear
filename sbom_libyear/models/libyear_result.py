from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .component import Component


@dataclass
class LibyearResult:
    component: Component
    current_version: str
    latest_version: str
    current_date: Optional[datetime]
    latest_date: Optional[datetime]
    years_behind: float
    error: Optional[str] = None