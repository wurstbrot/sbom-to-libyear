import json
from typing import List

from ..models import Component
from .base import SBOMParser


class CycloneDXJSONParser(SBOMParser):
    def can_parse(self, content: str) -> bool:
        try:
            if content.strip().startswith('{'):
                data = json.loads(content)
                return 'bomFormat' in data
        except:
            pass
        return False

    def parse(self, content: str) -> List[Component]:
        cyclonedx_data = json.loads(content)
        components = []
        
        for component in cyclonedx_data.get('components', []):
            name = component.get('name', '')
            version = component.get('version', '')
            purl = component.get('purl', '')
            
            package_type = 'unknown'
            group_id = None
            artifact_id = None
            
            if purl:
                package_type, group_id, artifact_id = self._parse_purl(purl)
                
            if name and version:
                components.append(Component(
                    name=name,
                    version=version,
                    package_type=package_type,
                    purl=purl,
                    group_id=group_id,
                    artifact_id=artifact_id
                ))
            elif name and not version:
                self.logger.warning(f"Skipping component '{name}' - no version information")
        
        self.logger.info(f"Parsed {len(components)} components from CycloneDX JSON")
        return components