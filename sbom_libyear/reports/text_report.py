from ..models import LibyearReport
from .base import ReportGenerator


class TextReportGenerator(ReportGenerator):
    def _format_report(self, report: LibyearReport) -> str:
        avg_per_component = f"{report.total_libyear/report.successful_analyses:.2f} years" if report.successful_analyses > 0 else "N/A (no successful analyses)"
        
        text_report = f"""
SBOM Libyear Analysis Report
============================

Summary:
- Analyzed components: {report.total_components}
- Successfully analyzed: {report.successful_analyses}
- Failed: {report.failed_analyses}
- Total libyear: {report.total_libyear:.2f} years
- Average per component: {avg_per_component}

Breakdown by Package Manager:
------------------------------------
"""
        
        for pkg_type, stats in report.breakdown_by_package_manager.items():
            avg_stat = f"{stats['total_libyear']/stats['successful_count']:.2f} years" if stats['successful_count'] > 0 else "N/A"
            text_report += f"""
{pkg_type.upper()}:
  - Components: {stats['component_count']}
  - Successful: {stats['successful_count']}
  - Failed: {stats['failed_count']}
  - Libyear: {stats['total_libyear']:.2f} years
  - Average: {avg_stat}
"""
        
        text_report += """
Detailed Results:
------------------------
"""
        
        sorted_components = sorted(report.components, key=lambda x: x['years_behind'], reverse=True)
        
        for component in sorted_components:
            if component['error']:
                text_report += f"[ERROR] {component['name']} v{component['current_version']} - {component['error']}\n"
            else:
                text_report += f"{component['name']} v{component['current_version']} -> v{component['latest_version']} "
                text_report += f"({component['years_behind']:.2f} years)\n"
        
        return text_report