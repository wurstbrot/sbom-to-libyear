from abc import ABC, abstractmethod
from typing import List, Tuple, Optional
import logging

from ..models import Component


class SBOMParser(ABC):
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def parse(self, content: str) -> List[Component]:
        pass

    @abstractmethod
    def can_parse(self, content: str) -> bool:
        pass

    def _parse_purl(self, purl: str) -> Tuple[str, Optional[str], Optional[str]]:
        if not purl or not purl.startswith('pkg:'):
            return 'unknown', None, None
        
        purl_parts = purl[4:]
        
        if '@' in purl_parts:
            purl_parts = purl_parts.split('@')[0]
        
        parts = purl_parts.split('/')
        
        package_type = parts[0] if parts else 'unknown'
        namespace = parts[1] if len(parts) > 1 else None
        name = parts[2] if len(parts) > 2 else None
        
        if package_type == 'maven':
            return package_type, namespace, name
        
        return package_type, namespace, name