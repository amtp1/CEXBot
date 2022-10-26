import re
from datetime import datetime as dt

from aiogram.types import CallbackQuery, Message
from aiogram.dispatcher.storage import FSMContext
from aiogram.utils.exceptions import BotKicked
from loguru import logger

from objects.globals import dp, config, bot
from keyboards.keyboards import S_CURR_COUPLE, PaymentKB
from models.models import *
from utils.converter import is_int
from commands import start


@dp.callback_query_handler(lambda query: query.data.startswith(("payment")))
async def payment(query: CallbackQuery, state: FSMContext):
    payment_method = re.sub("payment_", "", query.data)
    await state.update_data(method=payment_method)
    await query.message.edit_text(text="Введите сумму:")
    return await state.set_state("get_amount")


@dp.message_handler(state="get_amount")
async def get_amount(message: Message, state: FSMContext):
    if not is_int(message.text):
        return await message.answer(text="Введите корректное значение!")
    elif int(message.text) < 1:
        return await message.answer(text="Минимальное значение кратно единице!")
    await state.update_data(amount=message.text)
    data = await state.get_data()
    send = data.get("send")
    receive = data.get("receive")
    method = data.get("method")
    amount = data.get("amount")
    user = await User.objects.get(user_id=message.from_user.id)
    deal = Deal.objects.filter(user=user, send=send, receive=receive, method=method, amount=amount)
    if await deal.exists():
        deal = list(await deal.all())[-1]
        if not deal.finished:
            return await message.answer(text="Такая заявка находится в процессе ...")
        else:
            await create_deal(message, state, user, send, receive, method, amount)
    else:
        await create_deal(message, state, user, send, receive, method, amount)


@dp.message_handler(lambda message: message.chat.type == "group")
async def listen_admin_msg(message: Message):
    try:
        deal_id = re.split("#", re.split("\n", message.reply_to_message.text)[0])[1]
        link = message.text
        res = re.search("(?P<url>https?://[^\s]+)", link)
        if res: 
            link = res.group("url")
            link_page = (
                F"🔗Ссылка на оплату: {link}\n"
                F"❗️Ссылка действует 5 минут."
            )
            await bot.send_message(chat_id=message.from_user.id, text=link_page, reply_markup=PaymentKB.receipt(deal_id), reply_to_message_id=message.reply_to_message.message_id + 1)
            return await message.answer(text="Ссылка на оплату успешно отправлена.")
        else:
            await bot.send_message(chat_id=message.from_user.id, text=message.text, reply_to_message_id=message.reply_to_message.message_id + 1)
            return await message.answer(text="Сообщение успешно отправлено.")
    except IndexError:
        return await message.answer(text="На это сообщение нельзя отвечать!")


@dp.message_handler(lambda message: message.chat.type == "private")
async def listen_private_msg(message: Message):
    await bot.send_message(chat_id=config.group_id, text=message.text, reply_to_message_id=message.reply_to_message.message_id + 1)
    return await message.answer(text="Сообщение успешно отправлено!")


@dp.message_handler(lambda message: message.chat.type == "group", content_types=["photo"])
async def listen_admin_photo(message: Message, state: FSMContext):
    try:
        deal_id = re.split("#", re.split("\n", message.reply_to_message.caption)[0])[1]
        user_id = re.split(":", re.split("\n", message.reply_to_message.caption)[1])[1].replace(" ", "")
        path = rf"media/receipt/admins/{message.from_user.id}/deal_{deal_id}.jpg"
        await message.photo[-1].download(path)
        with open(path, "rb") as f:
            photo = f.read()
            f.close()
        deal = await Deal.objects.get(id=deal_id)
        await deal.update(finished=dt.utcnow())
        await bot.send_photo(chat_id=user_id, photo=photo, caption=f"<b>Чек от администратора. (Анкета #{deal_id})</b>", reply_to_message_id=message.reply_to_message.message_id + 1)
        return await message.answer(text="Чек успешно отправлен.")
    except IndexError:
        return await message.answer(text="На это сообщение нельзя ответчать!")
    except TypeError:
        return await message.answer(text="Нужно прикрепить ссылку!")


@dp.callback_query_handler(lambda query: query.data.startswith(("receipt")))
async def get_receipt(query: CallbackQuery, state: FSMContext):
    deal_id = re.sub("receipt_", "", query.data)
    await state.update_data(deal_id=deal_id)
    await query.message.edit_text(text="Прикрепите и отправьте фото чека:")
    return await state.set_state("get_receipt")


@dp.message_handler(content_types=["photo"], state="get_receipt")
async def read_user_receipt(message: Message, state: FSMContext):
    data = await state.get_data()
    deal_id = data.get("deal_id")
    path = rf"media/receipt/users/{message.from_user.id}/deal_{deal_id}.jpg"
    await message.photo[-1].download(path)
    with open(path, "rb") as f:
        photo = f.read()
        f.close()
    await state.finish()
    photo_caption = (
        f"<b>Чек анкеты #{deal_id}</b>\n"
        f"<b>ID пользователя: {message.from_user.id}</b>"
    )
    await bot.send_photo(chat_id=config.group_id, photo=photo, caption=photo_caption)
    return await message.answer(text="Ожидайте чек от администратора ...")


async def create_deal(message, state, user, send, receive, method, amount):
    await state.finish()
    deal = await Deal.objects.create(user=user, send=send, receive=receive, method=method, amount=amount)
    deal_page = (
        F"<b>Новая анкета #{deal.pk}</b>\n"
        F"⚙️Обмен: {S_CURR_COUPLE.get(send)} ➜ {S_CURR_COUPLE.get(receive)}\n"
        F"💳Метод: {method}\n"
        F"💰Сумма: {amount}"
    )
    try:
        await bot.send_message(config.group_id, deal_page)
        return await message.answer(text="Анкета отправлена. Ожидайте ответа ...")
    except BotKicked:
        logger.error(f"Bot kicked from chat: {config.group_id}")
        return await message.answer(text="При отправке возникла ошибка. Дождитесь её исправления ...")