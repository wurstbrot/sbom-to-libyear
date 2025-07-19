import json
from dataclasses import asdict

from ..models import LibyearReport
from .base import ReportGenerator


class JSONReportGenerator(ReportGenerator):
    def _format_report(self, report: LibyearReport) -> str:
        return json.dumps(asdict(report), indent=2, ensure_ascii=False, default=str)