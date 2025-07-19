import json
import logging
from typing import List

from ..models import Component
from .base import SBOMParser
from .cyclonedx_json import CycloneDXJSONParser
from .cyclonedx_xml import CycloneDXXMLParser
from .spdx_json import SPDXJSONParser


class SBOMParserContext:
    def __init__(self):
        self.parsers = [
            SPDXJSONParser(),
            CycloneDXJSONParser(),
            CycloneDXXMLParser()
        ]
        self.logger = logging.getLogger(self.__class__.__name__)

    def parse_file(self, filepath: str) -> List[Component]:
        with open(filepath, 'r', encoding='utf-8') as sbom_file:
            content = sbom_file.read()
        
        self.logger.info(f"Parsing SBOM file: {filepath}")
        
        for parser in self.parsers:
            if parser.can_parse(content):
                self.logger.info(f"Using parser: {parser.__class__.__name__}")
                return parser.parse(content)
        
        raise ValueError("SBOM format not recognized. Expected SPDX or CycloneDX in JSON or XML format.")

    def register_parser(self, parser: SBOMParser):
        self.parsers.append(parser)