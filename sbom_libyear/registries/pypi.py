from datetime import datetime
from typing import Optional, Tuple

from ..models import Component, RepositoryConfig
from .base import PackageRegistry


class PypiRegistry(PackageRegistry):
    def get_package_info(self, component: Component) -> Tuple[Optional[datetime], Optional[datetime], Optional[str]]:
        for repo in self.repositories:
            try:
                package_data = self._fetch_package_data(component, repo)
                if package_data:
                    return self._extract_version_info(package_data, component.version)
            except Exception as e:
                self.logger.debug(f"Error accessing PyPI registry {repo.name}: {e}")
                continue
        
        self.logger.warning(f"PyPI package '{component.name}' not found in any configured registry")
        return None, None, None

    def _fetch_package_data(self, component: Component, repository: RepositoryConfig) -> dict:
        url = f"{repository.url}/{component.name}/json"
        
        auth = None
        if repository.auth and 'username' in repository.auth and 'password' in repository.auth:
            auth = (repository.auth['username'], repository.auth['password'])
        
        response = self.http_client.get(url, auth=auth)
        
        if response.status_code == 200:
            return response.json()
        
        self.logger.debug(f"PyPI registry {repository.name} lookup failed for '{component.name}' - HTTP {response.status_code}")
        return None

    def _extract_version_info(self, package_data: dict, current_version: str) -> Tuple[Optional[datetime], Optional[datetime], Optional[str]]:
        releases = package_data.get('releases', {})
        
        current_date = None
        version_to_use = self._find_best_version_match(current_version, list(releases.keys()))
        
        if version_to_use and releases[version_to_use]:
            release_files = releases[version_to_use]
            for file_info in release_files:
                upload_time = file_info.get('upload_time') or file_info.get('upload_time_iso_8601')
                current_date = self._parse_pypi_date(upload_time)
                if current_date:
                    break
        
        latest_version = package_data.get('info', {}).get('version', '')
        latest_date = None
        if latest_version in releases and releases[latest_version]:
            release_files = releases[latest_version]
            for file_info in release_files:
                upload_time = file_info.get('upload_time') or file_info.get('upload_time_iso_8601')
                latest_date = self._parse_pypi_date(upload_time)
                if latest_date:
                    break
        
        return current_date, latest_date, latest_version

    def _parse_pypi_date(self, upload_time: str) -> Optional[datetime]:
        if not upload_time:
            return None
        try:
            if 'T' in upload_time:
                return datetime.fromisoformat(upload_time.replace('Z', '+00:00'))
            else:
                return datetime.strptime(upload_time, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return None