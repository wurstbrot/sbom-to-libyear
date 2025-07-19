import logging
from datetime import datetime
from typing import Optional, Tuple, Dict

from ..models import Component
from ..registries import PackageRegistryFactory
from ..utils import ConfigLoader


class RegistryManager:
    def __init__(self, config_loader: Optional[ConfigLoader] = None):
        self.config_loader = config_loader or ConfigLoader()
        self.registries: Dict[str, any] = {}
        self.logger = logging.getLogger(self.__class__.__name__)

    def get_package_info(self, component: Component) -> Tuple[Optional[datetime], Optional[datetime], Optional[str]]:
        self.logger.debug(f"Fetching info for {component.name} ({component.package_type})")
        
        if component.package_type == 'unknown':
            return self._auto_detect_package_info(component)
        
        registry = self._get_or_create_registry(component.package_type)
        if registry:
            return registry.get_package_info(component)
        
        return None, None, None

    def _get_or_create_registry(self, package_type: str):
        if package_type not in self.registries:
            try:
                repositories = self.config_loader.get_repositories(package_type)
                self.registries[package_type] = PackageRegistryFactory.create(package_type, repositories)
            except ValueError as e:
                self.logger.warning(f"Failed to create registry for {package_type}: {e}")
                return None
        
        return self.registries[package_type]

    def _auto_detect_package_info(self, component: Component) -> Tuple[Optional[datetime], Optional[datetime], Optional[str]]:
        java_indicators = [
            'jackson', 'guava', 'spring', 'apache', 'junit', 'slf4j', 'log4j',
            'commons', 'hibernate', 'dropwizard', 'jersey', 'joda', 'gson',
            'checker', 'error_prone', 'j2objc', 'animal-sniffer', 'jsr305'
        ]
        
        is_likely_java = any(indicator in component.name.lower() for indicator in java_indicators)
        
        package_types_to_try = []
        if is_likely_java:
            package_types_to_try.append('maven')
        
        package_types_to_try.extend(['pypi', 'npm'])
        
        for pkg_type in package_types_to_try:
            temp_component = Component(
                name=component.name,
                version=component.version,
                package_type=pkg_type,
                namespace=component.namespace,
                purl=component.purl,
                group_id=component.group_id,
                artifact_id=component.artifact_id
            )
            
            registry = self._get_or_create_registry(pkg_type)
            if registry:
                result = registry.get_package_info(temp_component)
                if result[0] is not None or result[1] is not None or (result[2] and result[2] != 'unknown'):
                    return result
        
        return None, None, None