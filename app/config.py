import json
from pathlib import Path
from typing import Dict, Any

from pydantic import BaseSettings, FilePath

CONFIG_PATH = Path('config.json')


def json_config_settings_source(settings: BaseSettings) -> Dict[str, Any]:
    encoding = settings.__config__.env_file_encoding
    return json.loads(CONFIG_PATH.read_text(encoding, errors='ignore'))


class Settings(BaseSettings):
    sms_activate_api_key: str
    names_path: FilePath
    proxies_path: FilePath
    client_id: int = 2274003
    client_secret: str = "hHbZxrka2uZ6jB1inYsH"

    class Config:
        env_file_encoding = 'utf-8'

        @classmethod
        def customise_sources(
            cls,
            init_settings,
            env_settings,
            file_secret_settings,
        ):
            return (
                init_settings,
                json_config_settings_source,
                file_secret_settings,
            )

    def save(self, path):
        json.dump(json.loads(self.json()), open(path, "w+"))


def first_time() -> Settings:
    sms_activate_api_key = input("API ключ от sms-activate: ")

    names_path = input("Путь до файла с именами [names.json]: ") or "names.json"

    proxies_path = input("Путь до файла с проксямих [proxies.txt]: ") or "proxies.txt"
    new_settings = Settings(
        sms_activate_api_key=sms_activate_api_key,
        names_path=names_path,
        proxies_path=proxies_path
    )
    new_settings.save("config.json")

    return new_settings


if not Path("config.json").exists():
    with open("config.json", "w+", encoding="utf-8") as file:
        file.write("{}")

    app_settings = first_time()
else:
    app_settings = Settings()
