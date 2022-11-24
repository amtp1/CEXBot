from aiogram.types import Message
from aiogram.dispatcher.storage import FSMContext

from objects.globals import dp
from utils.deal import get_deal


@dp.message_handler(lambda message: message.text == "Прикрепить чек", state="*")
async def attach_receipt(message: Message, state: FSMContext):
    deal = await get_deal(message.from_user.id)
    if not deal:
        return await message.answer(text="Вы не сможете прикрепить чек. Для этого нужно создать заявку!")
    await message.answer("Прикрепите и отправьте фото чека:")
    return await state.set_state("get_receipt")
