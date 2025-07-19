from typing import List

from ..models import RepositoryConfig
from .base import PackageRegistry
from .maven import MavenRegistry
from .npm import NpmRegistry
from .nuget import NugetRegistry
from .pypi import PypiRegistry


class PackageRegistryFactory:
    _registry_map = {
        'maven': MavenRegistry,
        'npm': NpmRegistry,
        'pypi': PypiRegistry,
        'nuget': NugetRegistry
    }

    @classmethod
    def create(cls, package_type: str, repositories: List[RepositoryConfig]) -> PackageRegistry:
        registry_class = cls._registry_map.get(package_type.lower())
        if not registry_class:
            raise ValueError(f"Unknown package type: {package_type}")
        
        return registry_class(repositories)

    @classmethod
    def register(cls, package_type: str, registry_class: type):
        cls._registry_map[package_type.lower()] = registry_class