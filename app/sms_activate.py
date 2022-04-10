import time

from smsactivateru import Sms, SmsTypes, SmsService, GetBalance, GetNumber, SetStatus, GetStatus


class ActivateException(BaseException):
    pass


class Activation:
    def __init__(self, wrapper: Sms):
        self.wrapper = wrapper
        activation = GetNumber(
            service=SmsService().VkCom,
            country=SmsTypes.Country.RU,
            operator=SmsTypes.Operator.any
        ).request(self.wrapper)
        self.id = activation.id
        self.phone = activation.phone_number

    def get_code(self) -> int:
        for _ in range(600):
            time.sleep(1)
            response = GetStatus(id=self.id).request(self.wrapper)
            if response['code']:
                self.sent()
                return response['code']

        self.cancel()
        raise ActivateException("Code was not delivered")

    def cancel(self) -> dict:
        return SetStatus(
            id=self.id,
            status=SmsTypes.Status.Cancel
        ).request(self.wrapper)

    def sent(self) -> dict:
        return SetStatus(
            id=self.id,
            status=SmsTypes.Status.SmsSent
        ).request(self.wrapper)


class SmsActivate:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.wrapper = Sms(api_key)

    def get_balance(self) -> int:
        return GetBalance().request(self.wrapper)

    def get_activation(self) -> Activation:
        return Activation(self.wrapper)
