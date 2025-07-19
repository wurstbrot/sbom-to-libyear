from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, Tuple, List
import logging

from ..models import Component, RepositoryConfig
from ..utils.http_client import HttpClient


class PackageRegistry(ABC):
    def __init__(self, repositories: List[RepositoryConfig]):
        self.repositories = repositories
        self.http_client = HttpClient()
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def get_package_info(self, component: Component) -> Tuple[Optional[datetime], Optional[datetime], Optional[str]]:
        pass

    @abstractmethod
    def _fetch_package_data(self, component: Component, repository: RepositoryConfig) -> dict:
        pass

    def _normalize_version(self, version: str) -> str:
        if version.lower().startswith('v'):
            version = version[1:]
        
        if '+' in version:
            version = version.split('+')[0]
        
        return version.strip()

    def _find_best_version_match(self, requested_version: str, available_versions: List[str]) -> Optional[str]:
        normalized_requested = self._normalize_version(requested_version)
        
        if requested_version in available_versions:
            return requested_version
        
        if normalized_requested in available_versions:
            return normalized_requested
        
        return None