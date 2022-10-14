import re

from aiogram.types import CallbackQuery
from aiogram.dispatcher.storage import FSMContext
from keyboards.keyboards import PaymentKB

from objects.globals import dp


@dp.callback_query_handler(lambda query: query.data.startswith(("receive")))
async def receive(query: CallbackQuery, state: FSMContext):
    currency = re.sub("receive_", "", query.data)
    await state.update_data(receive=currency)
    data = await state.get_data()
    return await query.message.edit_text(text="Варианты приема валюты", reply_markup=PaymentKB(data).payment_keyboard())
