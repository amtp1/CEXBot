from aiogram import Dispatcher, Bot

from config.config import Config

config = Config()  # Init config obj.

bot: Bot = None  # Set bot object without initialize.
dp: Dispatcher = None  # Set dispatcher object without initialize.
