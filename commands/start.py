from aiogram.types import Message
from aiogram.dispatcher.storage import FSMContext

from objects.globals import dp
from models.models import User
from keyboards.keyboards import CurrencyKB


@dp.message_handler(commands="start", state="*")
async def start(message: Message, state: FSMContext):
    await state.finish()
    user_id = message.from_user.id
    user = User.objects.filter(user_id=user_id)
    if not await user.exists():
        await User.objects.create(user_id=user_id, username=message.from_user.username, first_name=message.from_user.first_name, last_name=message.from_user.last_name)
    return await message.answer(text="Приветствую, я бот обменник :) Что вы отправляете?", reply_markup=CurrencyKB().send_keyboard())
