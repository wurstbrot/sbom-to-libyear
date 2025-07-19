import json
from typing import List

from ..models import Component
from .base import SBOMParser


class SPDXJSONParser(SBOMParser):
    def can_parse(self, content: str) -> bool:
        try:
            if content.strip().startswith('{'):
                data = json.loads(content)
                return 'spdxVersion' in data
        except:
            pass
        return False

    def parse(self, content: str) -> List[Component]:
        spdx_data = json.loads(content)
        components = []
        
        for package in spdx_data.get('packages', []):
            name = package.get('name', '')
            version = package.get('versionInfo', '')
            
            package_type = self._determine_package_type(package)
            
            if name and version:
                components.append(Component(
                    name=name,
                    version=version,
                    package_type=package_type
                ))
        
        self.logger.info(f"Parsed {len(components)} components from SPDX JSON")
        return components

    def _determine_package_type(self, package: dict) -> str:
        download_location = package.get('downloadLocation', '')
        
        if 'npmjs.org' in download_location:
            return 'npm'
        elif 'pypi.org' in download_location:
            return 'pypi'
        elif 'maven' in download_location or 'mvnrepository' in download_location:
            return 'maven'
        elif 'nuget.org' in download_location:
            return 'nuget'
        
        name = package.get('name', '')
        if ':' in name:
            return 'maven'
        elif '.' in name and not name.endswith('.py'):
            return 'maven'
        
        return 'unknown'