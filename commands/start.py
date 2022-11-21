from aiogram.types import Message
from aiogram.utils.exceptions import ChatNotFound
from aiogram.dispatcher.storage import FSMContext

from objects.globals import dp, bot, config
from models.models import User
from keyboards.keyboards import StartKB, CurrencyKB
from utils.order import check_order

from loguru import logger


@dp.message_handler(commands="start", state="*")
async def start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    try:
        response = await bot.get_chat_member(config.sub_group_id, user_id)
        if response.status == "left":
            return await message.answer(text="Чтобы использовать бот нужно вступить в группу.", reply_markup=StartKB.subscribe_keyboard())
    except ChatNotFound as e:
        return logger.error("%s: %s" % (e, config.sub_group_id,))

    user = User.objects.filter(user_id=user_id)
    if not await user.exists():
        await User.objects.create(user_id=user_id, username=message.from_user.username,
                                  first_name=message.from_user.first_name, last_name=message.from_user.last_name)
    else:
        await check_order(message, state)
    start_page = "Привет! Я бот - обменник. Помогу сделать перевод, обмен валют и/или оплатить сервис зарубежом и/или в России, минуя все ограничения!"
    return await message.answer(text=start_page, reply_markup=StartKB.start_keyboard())


@dp.message_handler(lambda message: message.text == "СТАРТ", state="*")
async def exchange(message: Message, state: FSMContext):
    await state.finish()  # Finish state
    return await message.answer(text="Приветствую, я бот обменник :) Что вы отправляете?", reply_markup=CurrencyKB.send_keyboard())
