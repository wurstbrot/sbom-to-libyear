import logging
import os
import yaml
from pathlib import Path
from typing import Dict, List, Optional

from ..models import RepositoryConfig


class ConfigLoader:
    _instance = None
    _config = None

    def __new__(cls, config_path: Optional[str] = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, config_path: Optional[str] = None):
        if ConfigLoader._config is None:
            self.logger = logging.getLogger(self.__class__.__name__)
            self.config_path = config_path or self._find_config_file()
            ConfigLoader._config = self._load_config()

    def _find_config_file(self) -> str:
        search_paths = [
            Path.cwd() / "config.yaml",
            Path.cwd() / "config.yml",
            Path.home() / ".sbom-libyear" / "config.yaml",
            Path.home() / ".sbom-libyear" / "config.yml"
        ]
        
        for path in search_paths:
            if path.exists():
                return str(path)
        
        return str(Path.cwd() / "config.yaml")

    def _load_config(self) -> Dict:
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r') as f:
                    config = yaml.safe_load(f)
                    self._expand_env_vars(config)
                    return config
        except Exception as e:
            self.logger.warning(f"Failed to load config from {self.config_path}: {e}")
        
        return self._get_default_config()

    def _expand_env_vars(self, config: Dict) -> None:
        for key, value in config.items():
            if isinstance(value, dict):
                self._expand_env_vars(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        self._expand_env_vars(item)
            elif isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                env_var = value[2:-1]
                config[key] = os.environ.get(env_var, value)

    def _get_default_config(self) -> Dict:
        return {
            "repositories": {
                "maven": [{
                    "name": "maven-central",
                    "url": "https://repo1.maven.org/maven2",
                    "search_url": "https://search.maven.org/solrsearch/select",
                    "enabled": True,
                    "priority": 1
                }],
                "npm": [{
                    "name": "npm-registry",
                    "url": "https://registry.npmjs.org",
                    "enabled": True,
                    "priority": 1
                }],
                "pypi": [{
                    "name": "pypi",
                    "url": "https://pypi.org/pypi",
                    "enabled": True,
                    "priority": 1
                }],
                "nuget": [{
                    "name": "nuget",
                    "url": "https://api.nuget.org/v3-flatcontainer",
                    "enabled": True,
                    "priority": 1
                }]
            },
            "http": {
                "timeout": 10,
                "retries": 3,
                "user_agent": "sbom-libyear-calculator/1.0"
            }
        }

    def get_repositories(self, package_type: str) -> List[RepositoryConfig]:
        repos = ConfigLoader._config.get("repositories", {}).get(package_type, [])
        enabled_repos = [
            RepositoryConfig(**repo) for repo in repos 
            if repo.get("enabled", True)
        ]
        return sorted(enabled_repos, key=lambda x: x.priority)

    def get_http_config(self) -> Dict:
        return ConfigLoader._config.get("http", {})

    def get_proxy_config(self) -> Optional[Dict]:
        return ConfigLoader._config.get("proxy")