from datetime import datetime
from typing import Optional, Tuple

from ..models import Component, RepositoryConfig
from .base import PackageRegistry


class NugetRegistry(PackageRegistry):
    def get_package_info(self, component: Component) -> Tuple[Optional[datetime], Optional[datetime], Optional[str]]:
        for repo in self.repositories:
            try:
                package_data = self._fetch_package_data(component, repo)
                if package_data:
                    return self._extract_version_info(package_data)
            except Exception as e:
                self.logger.debug(f"Error accessing NuGet registry {repo.name}: {e}")
                continue
        
        self.logger.warning(f"NuGet package '{component.name}' not found in any configured registry")
        return None, None, None

    def _fetch_package_data(self, component: Component, repository: RepositoryConfig) -> dict:
        url = f"{repository.url}/{component.name.lower()}/index.json"
        
        auth = None
        if repository.auth and 'username' in repository.auth and 'password' in repository.auth:
            auth = (repository.auth['username'], repository.auth['password'])
        
        response = self.http_client.get(url, auth=auth)
        
        if response.status_code == 200:
            return response.json()
        
        self.logger.debug(f"NuGet registry {repository.name} lookup failed for '{component.name}' - HTTP {response.status_code}")
        return None

    def _extract_version_info(self, package_data: dict) -> Tuple[Optional[datetime], Optional[datetime], Optional[str]]:
        available_versions = package_data.get('versions', [])
        
        if not available_versions:
            return None, None, None
        
        latest_version = available_versions[-1]
        
        return None, None, latest_version