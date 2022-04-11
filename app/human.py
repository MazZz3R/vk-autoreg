import json
import random
import secrets
from typing import List, Dict, Optional

import vk_api

from app_logger import get_logger
from config import app_settings

logger = get_logger(__name__)
import requests
logger.info("Выгрузка базы имён")
with app_settings.names_path.open() as file:
    data: Dict[str, Dict[str, List[str]]] = json.load(file)

class HumanSignupError(Exception):
    pass

class Human:
    def __init__(
            self,
            sex: Optional[int] = None,
            first_name: Optional[str] = None,
            last_name: Optional[str] = None,
            password: Optional[str] = None,
            birthday: Optional[str] = None
    ):
        self.sex = sex or random.randint(1, 2)  # 1 - female; 2 - male
        self.first_name = first_name or random.choice(data[str(self.sex)]["first_names"])
        self.last_name = last_name or random.choice(data[str(self.sex)]["last_names"])
        self.password = password or secrets.token_urlsafe(32)
        self.birthday = birthday or f"{random.randint(1, 27)}.{random.randint(1, 12)}.{random.randint(1980, 2000)}"

    def __repr__(self):
        return f"<Human: name={self.first_name} {self.last_name} sex={self.sex}" \
         "birthday={self.birthday}password={self.password}> "


class VkHuman(Human):
    @staticmethod
    def captcha_handler(captcha):
        key = input(f"Введите капчу {captcha.get_url()}: ")
        return captcha.try_again(key)

    def __init__(self, phone: str, proxy: str, *args, **kwargs):
        self.vk_session = vk_api.VkApi(captcha_handler=self.captcha_handler)
        self.vk_session.http.proxies = {
            "http": f"{proxy}",
            "https": f"{proxy}"
        }
        self.proxy = proxy
        self.vk = self.vk_session.get_api()
        self.phone = phone
        super().__init__(*args, **kwargs)

    def signup(self):
        try:
            response = self.vk.auth.signup(
                client_id=app_settings.client_id,
                client_secret=app_settings.client_secret,
                phone=self.phone,
                first_name=self.first_name,
                last_name=self.last_name,
                birthday=self.birthday,
                password=self.password,
                sex=self.sex
            )
            return response
        except vk_api.exceptions.ApiError as error:
            logger.error(f"Ошибка при создании аккаунта: \n{str(error)}")

            if "1004" in str(error) or "Invalid phone number" in str(error) or \
                    "One of the parameters specified was missing or invalid: can't accept this phone" in str(error) or \
                    'Flood control: sms sent limit' in str(error):
                print("Номер не доступен для регистрации")
                logger.error("Номер не доступен для регистрации")

            elif "User authorization failed: no access_token passed" in str(error):
                print("Аккаунт был забанен при регистрации.")
                logger.error("Аккаунт был забанен при регистрации.")

            else:
                print("Неизвестная ошибка, отправьте лог разработчику.")
                print(error)
            raise HumanSignupError("Bad phone")

        except (requests.exceptions.ProxyError, requests.exceptions.ConnectionError) as error:
            print(error)
            print(f"Bad proxy {self.proxy}")
            logger.error(f"Bad proxy {self.proxy}")

    def confirm(self, code: int):
        return self.vk.auth.confirm(
            client_id=app_settings.client_id,
            client_secret=app_settings.client_secret,
            phone=self.phone,
            password=self.password,
            code=code
        )

    def auth(self):
        self.vk_session.login = self.phone
        self.vk_session.password = self.password
        self.vk_session.auth()
        self.vk = self.vk_session.get_api()

    @property
    def token(self):
        return self.vk_session.token

    def subscribe(self, items: List[int]):
        for item_id in items:
            if item_id < 0:
                self.vk.groups.join(group_id=item_id)
            else:
                self.vk.friends.add(user_id=item_id)
