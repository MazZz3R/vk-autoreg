import json
import random
import secrets
from typing import List, Dict

import vk_api

from config import app_settings

with app_settings.names_path.open() as file:
    data: Dict[str, Dict[str, List[str]]] = json.load(file)


class Human:
    def __init__(self):
        self.sex = random.randint(1, 2)  # 1 - female; 2 - male
        self.first_name = random.choice(data[str(self.sex)]["first_names"])
        self.last_name = random.choice(data[str(self.sex)]["last_names"])
        self.password = secrets.token_urlsafe(32)
        self.birthday = f"{random.randint(1, 27)}.{random.randint(1, 12)}.{random.randint(1980, 2000)}"

    def __repr__(self):
        return f"<Human: {self.first_name} {self.last_name}\\{self.sex}\\{self.birthday}\\{self.password}>"


class VkHuman(Human):
    @staticmethod
    def captcha_handler(captcha):
        key = input(f"Введите капчу {captcha.get_url()}: ")
        return captcha.try_again(key)

    def __init__(self, phone: str, proxy: str):
        self.vk_session = vk_api.VkApi(captcha_handler=self.captcha_handler)
        self.vk_session.http.proxies = {
            "http": f"http://{proxy}",
            "https": f"https://{proxy}"
        }

        self.vk = self.vk_session.get_api()
        self.phone = phone
        super().__init__()

    def auth(self):
        self.vk_session.login = self.phone
        self.vk_session.password = self.password
        self.vk_session.auth()
        self.vk = self.vk_session.get_api()

    def subscribe(self, items: List[int]):
        for item_id in items:
            if item_id < 0:
                self.vk.groups.join(group_id=item_id)
            else:
                self.vk.friends.add(user_id=item_id)
