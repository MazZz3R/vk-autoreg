import time

from smsactivateru import Sms, SmsTypes, SmsService, GetBalance, GetNumber, SetStatus, GetStatus
from smsactivateru import errors

from config import app_settings
from app_logger import get_logger
logger = get_logger(__name__)


class ActivateException(BaseException):
    pass


class Activation:
    def __init__(self, wrapper: Sms):
        self.wrapper = wrapper
        try:
            activation = GetNumber(
                service=SmsService().VkCom,
                country=SmsTypes.Country.RU
            ).request(self.wrapper)
        except errors.ErrorsModel as e:
            logger.error(f"При получении номера произошла ошибка: {e}")
            print(e.message)
            exit(0)
        else:
            self.id = activation.id
            self.phone = activation.phone_number

    def get_code(self) -> int:
        for _ in range(100):
            time.sleep(1)
            response = GetStatus(id=self.id).request(self.wrapper)
            if response['code']:
                self.end()
                return response['code']

        self.cancel()
        raise ActivateException("Код не пришёл")

    def __repr__(self):
        return f"<Activation: id={self.id} phone={self.phone}>"

    def cancel(self) -> dict:
        return SetStatus(
            id=self.id,
            status=SmsTypes.Status.Cancel
        ).request(self.wrapper)

    def end(self) -> dict:
        return SetStatus(
            id=self.id,
            status=SmsTypes.Status.End
        ).request(self.wrapper)


class SmsActivate:
    def __init__(self, api_key: str = app_settings.sms_activate_api_key):
        self.api_key = api_key
        try:
            self.wrapper = Sms(api_key)
        except errors.ErrorsModel as e:
            print(e.message)
            exit(0)
        else:
            self.wrapper.url = "https://sms-activate.ru/stubs/handler_api.php"

    def get_balance(self) -> int:
        return GetBalance().request(self.wrapper)

    def get_activation(self) -> Activation:
        return Activation(self.wrapper)
