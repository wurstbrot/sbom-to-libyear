import xml.etree.ElementTree as ET
from typing import List

from ..models import Component
from .base import SBOMParser


class CycloneDXXMLParser(SBOMParser):
    def can_parse(self, content: str) -> bool:
        return content.strip().startswith('<') and 'cyclonedx' in content.lower()

    def parse(self, content: str) -> List[Component]:
        root = ET.fromstring(content)
        components = []
        
        ns = {'': 'http://cyclonedx.org/schema/bom/1.4'}
        if root.tag.startswith('{'):
            ns_uri = root.tag[1:].split('}')[0]
            ns = {'bom': ns_uri}
        
        for component in root.findall('.//bom:component', ns):
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
        
        self.logger.info(f"Parsed {len(components)} components from CycloneDX XML")
        return components