from aiogram.types import Message
from aiogram.utils.exceptions import ChatNotFound

from keyboards.keyboards import StartKB
from objects.globals import bot, config
from loguru import logger


async def check_subscribe(message: Message):
    group_id = config.sub_group_id
    try:
        response = await bot.get_chat_member(group_id, message.from_user.id)
        if response.status == "left":
            await message.answer(text="Чтобы использовать бот нужно вступить в группу.",
                                 reply_markup=StartKB.subscribe_keyboard())
            return (False, False)
        else:
            return (True, False)
    except ChatNotFound as e:
        logger.error("%s: %s" % (e, group_id,))
        return (False, True)
