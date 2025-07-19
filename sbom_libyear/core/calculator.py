import logging
from typing import List, Optional

from ..models import LibyearResult
from ..parsers import SBOMParserContext
from ..utils import ConfigLoader
from .registry_manager import RegistryManager


class LibyearCalculator:
    def __init__(self, config_loader: Optional[ConfigLoader] = None):
        self.config_loader = config_loader or ConfigLoader()
        self.parser_context = SBOMParserContext()
        self.registry_manager = RegistryManager(self.config_loader)
        self.logger = logging.getLogger(self.__class__.__name__)

    def calculate_from_sbom(self, filepath: str) -> List[LibyearResult]:
        components = self.parser_context.parse_file(filepath)
        results = []
        
        self.logger.info(f"Analyzing {len(components)} components...")
        
        for i, component in enumerate(components, 1):
            self.logger.info(f"[{i}/{len(components)}] Processing {component.name}...")
            
            current_date, latest_date, latest_version = self.registry_manager.get_package_info(component)
            
            years_behind = 0.0
            libyear_error = None
            
            if current_date and latest_date:
                delta = latest_date - current_date
                years_behind = delta.days / 365.25
            elif latest_version and latest_version != 'unknown':
                libyear_error = f"Release dates unavailable from registry, latest version: {latest_version}"
                years_behind = 0.0
            else:
                libyear_error = "Unable to retrieve version or release date information from package registry"
            
            results.append(LibyearResult(
                component=component,
                current_version=component.version,
                latest_version=latest_version or 'unknown',
                current_date=current_date,
                latest_date=latest_date,
                years_behind=years_behind if years_behind > 0 else 0,
                error=libyear_error
            ))
        
        return results