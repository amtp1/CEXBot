from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher.storage import FSMContext
from aiogram.utils.exceptions import ChatNotFound

from keyboards.keyboards import StartKB
from models.models import User
from utils.order import check_order
from objects.globals import bot, config, dp
from loguru import logger


async def check_subscribe(message):
    group_id = config.sub_group_id
    try:
        response = await bot.get_chat_member(group_id, message.from_user.id)
        if response.status == "left":
            await bot.send_message(message.from_user.id,
                                   text="Чтобы использовать бот нужно вступить в группу.",
                                   reply_markup=StartKB.subscribe_keyboard())
            return (False, False)
        else:
            return (True, False)
    except ChatNotFound as e:
        logger.error("%s: %s" % (e, group_id,))
        return (False, True)

@dp.callback_query_handler(lambda query: query.data == "check_subscribe")
async def check_subscribe_cb(query: CallbackQuery, state: FSMContext):
    status, is_error = await check_subscribe(query)
    if status:
        user = User.objects.filter(user_id=query.from_user.id)
        if not await user.exists():
            await User.objects.create(user_id=query.from_user.id, username=query.from_user.username,
                                      first_name=query.from_user.first_name, last_name=query.from_user.last_name)
        else:
            await check_order(query.message, state)
        start_page = ("Привет! Я бот - обменник. Помогу сделать перевод, обмен валют и/или оплатить сервис зарубежом "
                      "и/или в России, минуя все ограничения!")
        return await query.message.answer(text=start_page, reply_markup=StartKB.start_keyboard())
