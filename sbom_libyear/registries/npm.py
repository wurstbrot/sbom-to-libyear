from datetime import datetime
from typing import Optional, Tuple

from ..models import Component, RepositoryConfig
from .base import PackageRegistry


class NpmRegistry(PackageRegistry):
    def get_package_info(self, component: Component) -> Tuple[Optional[datetime], Optional[datetime], Optional[str]]:
        for repo in self.repositories:
            try:
                package_data = self._fetch_package_data(component, repo)
                if package_data:
                    return self._extract_version_info(package_data, component.version)
            except Exception as e:
                self.logger.debug(f"Error accessing NPM registry {repo.name}: {e}")
                continue
        
        self.logger.warning(f"NPM package '{component.name}' not found in any configured registry")
        return None, None, None

    def _fetch_package_data(self, component: Component, repository: RepositoryConfig) -> dict:
        url = f"{repository.url}/{component.name}"
        
        auth_headers = {}
        auth = None
        
        if repository.auth:
            if 'token' in repository.auth:
                auth_headers['Authorization'] = f"Bearer {repository.auth['token']}"
            elif 'username' in repository.auth and 'password' in repository.auth:
                auth = (repository.auth['username'], repository.auth['password'])
        
        response = self.http_client.get(url, headers=auth_headers, auth=auth)
        
        if response.status_code == 200:
            return response.json()
        
        self.logger.debug(f"NPM registry {repository.name} lookup failed for '{component.name}' - HTTP {response.status_code}")
        return None

    def _extract_version_info(self, package_data: dict, current_version: str) -> Tuple[Optional[datetime], Optional[datetime], Optional[str]]:
        time_data = package_data.get('time', {})
        
        current_date = None
        if current_version in time_data:
            current_date = datetime.fromisoformat(time_data[current_version].replace('Z', '+00:00'))
        
        latest_version = package_data.get('dist-tags', {}).get('latest', '')
        latest_date = None
        if latest_version in time_data:
            latest_date = datetime.fromisoformat(time_data[latest_version].replace('Z', '+00:00'))
        
        return current_date, latest_date, latest_version