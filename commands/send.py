import re

from aiogram.types import CallbackQuery
from aiogram.dispatcher.storage import FSMContext

from objects.globals import dp
from keyboards.keyboards import CurrencyKB


@dp.callback_query_handler(lambda query: query.data.startswith(("send")))
async def send(query: CallbackQuery, state: FSMContext):
    currency = re.sub("send_", "", query.data)
    await state.update_data(send=currency)
    return await query.message.edit_text(text="Что вы получаете?", reply_markup=CurrencyKB(currency=currency).receive_keyboard())
