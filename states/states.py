from aiogram.dispatcher.filters.state import StatesGroup, State


class Currency(StatesGroup):
    send = State()
    receive = State()


class Payment(StatesGroup):
    get_amount = State()
    get_technical_task = State()
    method = State()
    deal_id = State()


class Money(StatesGroup):
    amount = State()


class Receipt(StatesGroup):
    get_receipt = State()


class Receive(StatesGroup):
    receive = State()


class Chat(StatesGroup):
    message = State()
