from dataclasses import dataclass
from typing import Dict, List


@dataclass
class LibyearReport:
    total_libyear: float
    total_components: int
    successful_analyses: int
    failed_analyses: int
    breakdown_by_package_manager: Dict[str, Dict[str, float]]
    components: List[Dict]
    errors: List[Dict]