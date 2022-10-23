from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

S_CURR_COUPLE = {
    "euro": "Евро",
    "dollar": "Доллары",
    "rouble": "Рубли",
    "tenge": "Тенге"
}  # Send currency couple

R_CURR_COUPLE = {
    "euro": {"rouble": "Рубли", "product||service": "Оплата товара/сервиса"},
    "dollar": {"rouble": "Рубли", "product||service": "Оплата товара/сервиса"},
    "rouble": {"euro": "Евро", "dollar": "Доллары", "tenge": "Тенге", "product||service": "Оплата товара/сервиса"},
    "tenge": {"rouble": "Рубли", "product||service": "Оплата товара/сервиса"}
}  # Receive currency couple


class StartKB:
    @staticmethod
    def start_keyboard():
        start_choice = ReplyKeyboardMarkup(
            resize_keyboard=True, keyboard=[[KeyboardButton(text="СТАРТ")]]
        )
        return start_choice


class CurrencyKB:
    def __init__(self, currency=None):
        self.currency = currency

    @staticmethod
    def send_keyboard():
        send_choice = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(
                text=v, callback_data=f"send_{k}")] for k, v in S_CURR_COUPLE.items()]
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

    def payment_keyboard(self):
        payment_choice = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(
                text=m, callback_data=f"payment_{m}")] for m in self.payment_method()]
        )
        return payment_choice

    def payment_method(self):
        if self.send == "euro" and self.receive == "rouble":
            payment_method = ["Revolut", "PayPal",
                              "TransferWise", "Instant Iban"]
        elif self.send == "dollar" and self.receive == "rouble":
            payment_method = ["Revolut", "PayPal",
                              "TransferWise", "Inside US Transfers"]
        elif self.send == "rouble" and self.receive in ["euro", "dollar", "tenge"]:
            payment_method = ["Номер карты", "СБП Тинькофф", "Сбер", "Альфа"]
        elif self.send == "tenge" and self.receive == "rouble":
            payment_method = ["Перевод на карту", "Каспи"]
        else:
            payment_method = ["Unknow"]
        return payment_method

    @staticmethod
    def receipt(deal_id):
        receipt_chose = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="Прикрепить чек", callback_data=f"receipt_{deal_id}")]]
        )
        return receipt_chose
