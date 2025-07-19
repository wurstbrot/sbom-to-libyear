from abc import ABC, abstractmethod
from dataclasses import asdict
from typing import List

from ..models import LibyearResult, LibyearReport


class ReportGenerator(ABC):
    def generate(self, results: List[LibyearResult]) -> str:
        report = self._create_report_data(results)
        return self._format_report(report)

    def _create_report_data(self, results: List[LibyearResult]) -> LibyearReport:
        total_libyear = sum(r.years_behind for r in results if r.error is None)
        successful_analyses = len([r for r in results if r.error is None])
        failed_analyses = len([r for r in results if r.error is not None])
        
        package_manager_breakdown = {}
        for result in results:
            pkg_type = result.component.package_type
            if pkg_type not in package_manager_breakdown:
                package_manager_breakdown[pkg_type] = {
                    'total_libyear': 0.0,
                    'component_count': 0,
                    'successful_count': 0,
                    'failed_count': 0
                }
            
            package_manager_breakdown[pkg_type]['component_count'] += 1
            if result.error is None:
                package_manager_breakdown[pkg_type]['total_libyear'] += result.years_behind
                package_manager_breakdown[pkg_type]['successful_count'] += 1
            else:
                package_manager_breakdown[pkg_type]['failed_count'] += 1
        
        components_data = []
        for result in results:
            components_data.append({
                'name': result.component.name,
                'package_type': result.component.package_type,
                'current_version': result.current_version,
                'latest_version': result.latest_version,
                'years_behind': result.years_behind,
                'current_date': result.current_date.isoformat() if result.current_date else None,
                'latest_date': result.latest_date.isoformat() if result.latest_date else None,
                'purl': result.component.purl,
                'error': result.error
            })
        
        errors = []
        for result in results:
            if result.error:
                errors.append({
                    'component': result.component.name,
                    'package_type': result.component.package_type,
                    'version': result.current_version,
                    'error': result.error,
                    'purl': result.component.purl
                })
        
        return LibyearReport(
            total_libyear=total_libyear,
            total_components=len(results),
            successful_analyses=successful_analyses,
            failed_analyses=failed_analyses,
            breakdown_by_package_manager=package_manager_breakdown,
            components=components_data,
            errors=errors
        )

    @abstractmethod
    def _format_report(self, report: LibyearReport) -> str:
        pass