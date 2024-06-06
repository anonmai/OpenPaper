from src.component.config_manager import ConfigManager
from openai import OpenAI
import httpx


class Context:
    def __init__(self, config_path):
        self._config_path = config_path
        self._config_manager = ConfigManager(config_path)

    def get_client(self):
        config = self.get_config()
        proxies = config.get("proxies")
        openai_key = config.get("openai_key")
        client = OpenAI(api_key=openai_key, http_client=httpx.Client(proxies=proxies))
        return client

    def get_config(self):
        return self._config_manager.parse_config()

    def update_config(self, new_data: dict):
        self._config_manager.update_config(new_data)


