import requests
from typing import Optional, Dict, Any


class HttpClient:
    _instance = None
    _session = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if HttpClient._session is None:
            HttpClient._session = requests.Session()
            self.timeout = 10
            self.user_agent = 'sbom-libyear-calculator/1.0'
            HttpClient._session.headers.update({'User-Agent': self.user_agent})

    def configure(self, timeout: int, user_agent: str, proxies: Optional[Dict[str, str]] = None):
        self.timeout = timeout
        self.user_agent = user_agent
        HttpClient._session.headers.update({'User-Agent': user_agent})
        if proxies:
            HttpClient._session.proxies = proxies

    def get(self, url: str, params: Optional[Dict[str, Any]] = None, 
            headers: Optional[Dict[str, str]] = None,
            auth: Optional[tuple] = None) -> requests.Response:
        return HttpClient._session.get(
            url, 
            params=params, 
            headers=headers,
            auth=auth,
            timeout=self.timeout
        )

    def post(self, url: str, data: Optional[Dict[str, Any]] = None,
             json: Optional[Dict[str, Any]] = None,
             headers: Optional[Dict[str, str]] = None,
             auth: Optional[tuple] = None) -> requests.Response:
        return HttpClient._session.post(
            url,
            data=data,
            json=json,
            headers=headers,
            auth=auth,
            timeout=self.timeout
        )