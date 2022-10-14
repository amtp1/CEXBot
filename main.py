import asyncio

from loguru import logger
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from objects import globals
from objects.globals import config
from models.models import models, database


async def main():
    globals.bot: Bot = Bot(token=config.token, parse_mode="HTML")
    globals.dp: Dispatcher = Dispatcher(globals.bot, storage=MemoryStorage())

    bot_info: dict = await globals.bot.get_me()
    logger.info(F"Bot username: @{bot_info.username}, Bot ID: {bot_info.id}")

    await models.create_all()

    import commands

    await globals.dp.start_polling()

if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped!")
