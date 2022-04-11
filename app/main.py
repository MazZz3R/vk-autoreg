import app_logger

logger = app_logger.get_logger(__name__)
logger.info("Программа стартует")

from human import VkHuman, HumanSignupError
from sms_activate import SmsActivate, ActivateException
from config import app_settings
from threading import Thread

sms = SmsActivate()

logger.info("Выгрузка прокси")
with app_settings.proxies_path.open() as file:
    proxies = [proxy.strip() for proxy in file.readlines()]

log = open("log.txt", "a+")


def create_account(proxy: str):
    logger.info("Получение номера для активации")
    activation = sms.get_activation()
    logger.info(f"Activation: {activation}")
    phone = activation.phone

    logger.info("Создание human")
    human = VkHuman(proxy=proxy, phone=phone)
    logger.info(f"Human: {human}")

    logger.info("Регистрация...")
    try:
        human.signup()
    except HumanSignupError as e:
        activation.cancel()
        logger.error("Регистрация прервана, неверный номер телефона")
        return

    logger.info("Получение кода...")
    try:
        code = activation.get_code()
    except ActivateException as e:
        print("Ошибка в получении кода")
        logger.error(e)
        return

    logger.info(f"Подтверждение кода: {code}")
    human.confirm(code)

    logger.info(f"Запись в лог: \"{human.phone}:{human.password}:{human.token}\"")
    log.write(f"{human.phone}:{human.password}\n")


for proxy in proxies:
    thread = Thread(target=create_account, args=[proxy])
    thread.start()
