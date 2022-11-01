from aiogram.types import Message
from aiogram.dispatcher.storage import FSMContext

from objects.globals import dp


@dp.message_handler(lambda message: message.text == "Прикрепить чек", state="*")
async def attach_receipt(message: Message, state: FSMContext):
    await message.answer("Прикрепите и отправьте фото чека:")
    return await state.set_state("get_receipt")
