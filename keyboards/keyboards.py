from aiogram.types import (InlineKeyboardMarkup, InlineKeyboardButton,
                           ReplyKeyboardMarkup, KeyboardButton)

from objects.globals import config

S_CURR_COUPLE = {
    "euro": "Евро",
    "dollar": "Доллары",
    "rouble": "Рубли",
    "tenge": "Тенге",
    "product||service": "Оплата товара/сервиса"
}  # Send currency couple

R_CURR_COUPLE = {
    "euro": {"rouble": "Рубли", "product||service": "Оплата товара/сервиса"},
    "dollar": {"rouble": "Рубли", "product||service": "Оплата товара/сервиса"},
    "rouble": {"euro": "Евро", "dollar": "Доллары", "tenge": "Тенге", "product||service": "Оплата товара/сервиса"},
    "tenge": {"rouble": "Рубли", "product||service": "Оплата товара/сервиса"}
}  # Receive currency couple

PAYMENT_METHODS = [
    "Revolut", "PayPal", "TransferWise", "Instant Iban", "Inside US Transfers", "Номер карты",
    "СБП Тинькофф", "Сбер", "Альфа", "Перевод на карту", "Каспи"
]


class StartKB:
    @staticmethod
    def start_keyboard():
        start_choice = ReplyKeyboardMarkup(
            resize_keyboard=True, keyboard=[[KeyboardButton(text="СТАРТ")]]
        )
        return start_choice

    @staticmethod
    def subscribe_keyboard():
        subscribe_choice = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Перейти", url=config.sub_group_url)],
                [InlineKeyboardButton(text="Проверить подписку", callback_data="check_subscribe")]
            ]
        )
        return subscribe_choice


class CurrencyKB:
    def __init__(self, currency=None):
        self.currency = currency

    @staticmethod
    def send_keyboard():
        send_choice = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(
                text=v, callback_data=f"send_{k}")] for k, v in S_CURR_COUPLE.items() if not k == "product||service"]
        )
        return send_choice

    def receive_keyboard(self):
        receive_choice = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(
                text=v, callback_data=f"receive_{k}")] for k, v in R_CURR_COUPLE[self.currency].items()]
        )

        return receive_choice


class PaymentKB:
    def __init__(self, data=None):
        if data:
            self.send = data.get("send")
            self.receive = data.get("receive")

    def send_payment_keyboard(self):
        """Create payment method to InlineKeyboardMarkup"""

        payment_choice = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(
                text=m, callback_data=f"s_payment_{m}")] for m in self.send_payment_method()]
        )
        return payment_choice

    def receive_payment_keyboard(self):
        payment_choice = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(
                text=m, callback_data=f"r_payment_{m}")] for m in self.receive_payment_method()]
        )
        return payment_choice

    def send_payment_method(self):
        """Check payment method"""

        if self.send == "euro" and self.receive == "rouble":
            payment_method = ["Revolut", "PayPal",
                              "TransferWise", "Instant Iban", "Не знаю"]
        elif self.send == "dollar" and self.receive == "rouble":
            payment_method = ["Revolut", "PayPal",
                              "TransferWise", "Inside US Transfers", "Не знаю"]
        elif self.send == "rouble" and self.receive in ["euro", "dollar", "tenge"]:
            payment_method = ["Номер карты", "СБП Тинькофф", "Сбер", "Альфа", "Не знаю"]
        elif self.send == "tenge" and self.receive == "rouble":
            payment_method = ["Перевод на карту", "Каспи", "Не знаю"]
        else:
            payment_method = ["Техническое задание"]
        return payment_method

    def receive_payment_method(self):
        payment_methods = PAYMENT_METHODS[:]
        send_payment_method = self.send_payment_method()[:-1]
        [payment_methods.remove(m) for m in send_payment_method]
        return payment_methods

    @staticmethod
    def receipt():
        receipt_chose = ReplyKeyboardMarkup(
            resize_keyboard=True, keyboard=[[KeyboardButton(text="Прикрепить чек")],
                                            [KeyboardButton(text="СТАРТ")]]
        )
        return receipt_chose
