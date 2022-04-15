import app_logger
from human import VkHuman, HumanSignupError
from sms_activate import SmsActivate, ActivateException
from config import app_settings
from threading import Thread
from time import sleep


def main():
    sms = SmsActivate()

    logger.info("Выгрузка прокси")
    with app_settings.proxies_path.open(encoding='utf-8') as file:
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
        except HumanSignupError:
            activation.cancel()
            logger.error("Регистрация прервана, неверный номер телефона")
            return

        logger.info("Получение кода...")
        try:
            code = activation.get_code()
        except ActivateException as e:
            print("Ошибка в получении кода")
            activation.cancel()
            logger.error(e)
            return

        logger.info(f"Подтверждение кода: {code}")
        human.confirm(code)

        logger.info(f"Запись в лог: \"{human.phone}:{human.password}\"")
        log.write(f"{human.phone}:{human.password}\n")

    for proxy in proxies:
        thread = Thread(target=create_account, args=[proxy])
        sleep(2)
        thread.start()


if __name__ == "__main__":
    logger = app_logger.get_logger(__name__)
    logger.info("Программа стартует")
    main()
