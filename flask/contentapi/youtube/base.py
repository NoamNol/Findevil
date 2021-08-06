from abc import ABC


class BaseApi(ABC):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_service_name = "youtube"
        self.api_version = "v3"
