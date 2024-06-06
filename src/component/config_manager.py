from ruamel.yaml import YAML


class ConfigManager:
    def __init__(self, config_path="./config.yml"):
        self._config_path = config_path

    def parse_config(self) -> dict:
        with open(self._config_path, mode="rb") as f:
            yaml = YAML()
            data = yaml.load(f)
        return data

    def update_config(self, new: dict):
        config = self.parse_config()
        config.update(new)
        with open(self._config_path, 'w') as file:
            yaml = YAML()
            yaml.dump(config, file)
