import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Optional, Tuple

from ..models import Component, RepositoryConfig
from .base import PackageRegistry


class MavenRegistry(PackageRegistry):
    def get_package_info(self, component: Component) -> Tuple[Optional[datetime], Optional[datetime], Optional[str]]:
        group_id, artifact_id = self._extract_maven_coordinates(component)
        
        self.logger.debug(f"Maven lookup: {group_id}:{artifact_id}")
        
        for repo in self.repositories:
            try:
                result = self._fetch_from_repository(group_id, artifact_id, component.version, repo)
                if result[0] is not None or result[1] is not None or result[2] is not None:
                    return result
            except Exception as e:
                self.logger.debug(f"Error accessing Maven repository {repo.name}: {e}")
                continue
        
        self.logger.warning(f"Maven artifact '{group_id}:{artifact_id}' not found in any configured repository")
        return None, None, None

    def _fetch_package_data(self, component: Component, repository: RepositoryConfig) -> dict:
        pass

    def _extract_maven_coordinates(self, component: Component) -> Tuple[str, str]:
        if component.group_id and component.artifact_id:
            return component.group_id, component.artifact_id
        elif ':' in component.name:
            return component.name.split(':', 1)
        else:
            group_id = self._guess_group_id(component.name)
            return group_id, component.name

    def _guess_group_id(self, artifact_name: str) -> str:
        common_mappings = {
            'guava': 'com.google.guava',
            'commons-lang3': 'org.apache.commons',
            'commons-io': 'org.apache.commons',
            'junit': 'junit',
            'slf4j-api': 'org.slf4j',
            'log4j-core': 'org.apache.logging.log4j',
            'joda-time': 'joda-time',
            'gson': 'com.google.code.gson',
            'checker-compat-qual': 'org.checkerframework',
            'error_prone_annotations': 'com.google.errorprone',
            'j2objc-annotations': 'com.google.j2objc',
            'animal-sniffer-annotations': 'org.codehaus.mojo',
            'jsr305': 'com.google.code.findbugs'
        }
        
        return common_mappings.get(artifact_name, 'unknown')

    def _fetch_from_repository(self, group_id: str, artifact_id: str, current_version: str,
                               repo: RepositoryConfig) -> Tuple[Optional[datetime], Optional[datetime], Optional[str]]:
        auth = None
        if repo.auth and 'username' in repo.auth and 'password' in repo.auth:
            auth = (repo.auth['username'], repo.auth['password'])
        
        if repo.search_url:
            result = self._search_maven_central(group_id, artifact_id, current_version, repo, auth)
            if result[0] is not None or result[1] is not None or result[2] is not None:
                return result
        
        result = self._get_maven_metadata_dates(group_id, artifact_id, current_version, repo, auth)
        if result[0] is not None or result[1] is not None:
            latest_version = self._get_latest_version_from_metadata(group_id, artifact_id, repo, auth)
            return result[0], result[1], latest_version or 'unknown'
        
        return None, None, None

    def _search_maven_central(self, group_id: str, artifact_id: str, current_version: str,
                              repo: RepositoryConfig, auth: Optional[Tuple[str, str]]) -> Tuple[Optional[datetime], Optional[datetime], Optional[str]]:
        params = {
            'q': f'g:"{group_id}" AND a:"{artifact_id}"',
            'rows': 1,
            'wt': 'json'
        }
        
        response = self.http_client.get(repo.search_url, params=params, auth=auth)
        
        if response.status_code != 200:
            return None, None, None
        
        search_data = response.json()
        artifacts = search_data.get('response', {}).get('docs', [])
        
        if not artifacts:
            return None, None, None
        
        artifact = artifacts[0]
        latest_version = artifact.get('latestVersion', '')
        
        params = {
            'q': f'g:"{group_id}" AND a:"{artifact_id}"',
            'rows': 50,
            'wt': 'json',
            'core': 'gav'
        }
        
        versions_response = self.http_client.get(repo.search_url, params=params, auth=auth)
        if versions_response.status_code != 200:
            return None, None, latest_version
        
        versions_data = versions_response.json()
        version_records = versions_data.get('response', {}).get('docs', [])
        
        current_date = None
        latest_date = None
        
        for record in version_records:
            version = record.get('v', '')
            timestamp = record.get('timestamp', 0)
            
            if timestamp > 0:
                date = datetime.fromtimestamp(timestamp / 1000)
                
                if version == current_version:
                    current_date = date
                
                if version == latest_version:
                    latest_date = date
        
        if not current_date or not latest_date:
            fallback_result = self._get_maven_metadata_dates(
                group_id, artifact_id, current_version, repo, auth, latest_version
            )
            if not current_date:
                current_date = fallback_result[0]
            if not latest_date:
                latest_date = fallback_result[1]
        
        return current_date, latest_date, latest_version

    def _get_maven_metadata_dates(self, group_id: str, artifact_id: str,
                                  current_version: str, repo: RepositoryConfig,
                                  auth: Optional[Tuple[str, str]],
                                  latest_version: Optional[str] = None) -> Tuple[Optional[datetime], Optional[datetime]]:
        group_path = group_id.replace('.', '/')
        
        current_date = None
        latest_date = None
        
        current_version_url = f"{repo.url}/{group_path}/{artifact_id}/{current_version}/maven-metadata.xml"
        try:
            response = self.http_client.get(current_version_url, auth=auth)
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                timestamp = root.find('.//timestamp')
                if timestamp is not None and timestamp.text:
                    timestamp_str = timestamp.text.replace('.', '')
                    current_date = datetime.strptime(timestamp_str[:14], '%Y%m%d%H%M%S')
        except Exception:
            pass
        
        if latest_version:
            latest_version_url = f"{repo.url}/{group_path}/{artifact_id}/{latest_version}/maven-metadata.xml"
            try:
                response = self.http_client.get(latest_version_url, auth=auth)
                if response.status_code == 200:
                    root = ET.fromstring(response.content)
                    timestamp = root.find('.//timestamp')
                    if timestamp is not None and timestamp.text:
                        timestamp_str = timestamp.text.replace('.', '')
                        latest_date = datetime.strptime(timestamp_str[:14], '%Y%m%d%H%M%S')
            except Exception:
                pass
        
        if not latest_date:
            metadata_url = f"{repo.url}/{group_path}/{artifact_id}/maven-metadata.xml"
            try:
                response = self.http_client.get(metadata_url, auth=auth)
                if response.status_code == 200:
                    root = ET.fromstring(response.content)
                    
                    if not latest_date:
                        last_updated = root.find('.//lastUpdated')
                        if last_updated is not None and last_updated.text:
                            timestamp_str = last_updated.text[:14]
                            latest_date = datetime.strptime(timestamp_str, '%Y%m%d%H%M%S')
            except Exception:
                pass
        
        return current_date, latest_date

    def _get_latest_version_from_metadata(self, group_id: str, artifact_id: str,
                                          repo: RepositoryConfig, auth: Optional[Tuple[str, str]]) -> Optional[str]:
        group_path = group_id.replace('.', '/')
        metadata_url = f"{repo.url}/{group_path}/{artifact_id}/maven-metadata.xml"
        
        try:
            response = self.http_client.get(metadata_url, auth=auth)
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                
                release = root.find('.//release')
                if release is not None and release.text:
                    return release.text
                
                latest = root.find('.//latest')
                if latest is not None and latest.text:
                    return latest.text
                
                versions = root.findall('.//version')
                if versions:
                    version_list = [v.text for v in versions if v.text]
                    if version_list:
                        return version_list[-1]
        except Exception:
            pass
        
        return None