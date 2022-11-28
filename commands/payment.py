import re
from datetime import datetime as dt

from aiogram.types import CallbackQuery, Message
from aiogram.dispatcher.storage import FSMContext
from aiogram.utils.exceptions import BotKicked, BadRequest
from loguru import logger

from objects.globals import dp, config, bot
from keyboards.keyboards import S_CURR_COUPLE, PaymentKB, StartKB
from models.models import *
from utils.converter import is_int
from utils.deal import get_deal
from utils.file import read_local_file
from commands import start, attach_receipt


@dp.callback_query_handler(lambda query: query.data.startswith(("payment")))
async def payment(query: CallbackQuery, state: FSMContext):
    payment_method = re.sub("payment_", "", query.data)
    await state.update_data(method=payment_method)
    if payment_method == "Техническое задание":
        await query.message.edit_text(text="Напишите техническое задание:")
        return await state.set_state("get_technical_task")
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
    deal = Deal.objects.filter(
        user=user, send=send, receive=receive, method=method, amount=amount)
    if await deal.exists():
        deal = list(await deal.all())[-1]
        if not deal.finished and not deal.is_cancel:
            return await message.answer(text="Такая заявка находится в процессе ...\n"
                                        "Нажмите на команду /start для отмены заявки.")
        else:
            await create_deal(message, state, user, send, receive, method, amount, content=None,
                              is_technical_task=False)
    else:
        await create_deal(message, state, user, send, receive, method, amount, content=None, is_technical_task=False)


@dp.message_handler(state="get_technical_task")
async def get_technical_task(message: Message, state: FSMContext, amount=0.0):
    content = message.text
    user = await User.objects.get(user_id=message.from_user.id)
    data = await state.get_data()
    send = data.get("send")
    receive = data.get("receive")
    method = data.get("method")
    await create_deal(message=message, state=state, user=user, send=send, receive=receive,
                      method=method, amount=amount, is_technical_task=True, content=content)


@dp.message_handler(lambda message: message.chat.type in ("group", "supergroup",))
async def listen_admin_msg(message: Message, user_id=None):
    message_split = re.split(r"\n", message.reply_to_message.text)
    if len(message_split) > 1:
        user_id = re.sub("👤User ID: ", "", message_split[1])
    if user_id:
        try:
            await bot.send_message(chat_id=user_id, text=message.text)
        except BadRequest as e:
            logger.error(e)
        except Exception as e:
            logger.error(e)


@dp.message_handler(lambda message: message.chat.type == "private")
async def listen_private_msg(message: Message):
    message_page = (
        F"📍<b>ID заявки:</b> без заявки\n"
        F"👤<b>User ID:</b> {message.from_user.id}\n"
        F"🔗Username: @{message.from_user.username}\n"
        f"✉️<b>Сообщение:</b> {message.text}"
    )
    try:
        await bot.send_message(chat_id=config.main_group_id, text=message_page)
    except AttributeError:
        return await bot.send_message(chat_id=config.main_group_id, text=message_page)


@dp.message_handler(lambda message: message.chat.type in ("group", "supergroup",), content_types=["photo"])
async def listen_admin_photo(message: Message, state: FSMContext):
    try:
        deal_id = re.split("#", re.split(
            "\n", message.reply_to_message.caption)[0])[1]
        user_id = re.split(":", re.split("\n", message.reply_to_message.caption)[1])[1].replace(" ", "")
        path = rf"media/receipt/admins/{message.from_user.id}/deal_{deal_id}.jpg"
        await message.photo[-1].download(path)
        with open(path, "rb") as f:
            photo = f.read()
            f.close()
        await bot.send_photo(chat_id=user_id, photo=photo, caption=f"<b>Чек от администратора. (Заявка #{deal_id})</b>")
        return await finish_deal(message, state, deal_id)
    except IndexError:
        return await message.answer(text="На это сообщение нельзя ответчать!")
    except TypeError:
        return await message.answer(text="Некорректный формат!")


@dp.callback_query_handler(lambda query: query.data.startswith(("receipt")))
async def get_receipt(query: CallbackQuery, state: FSMContext):
    deal_id = re.sub("receipt_", "", query.data)
    await state.update_data(deal_id=deal_id)
    await query.message.edit_text(text="Прикрепите и отправьте фото чека:")
    return await state.set_state("get_receipt")


@dp.message_handler(state="get_receipt", content_types=["photo", "document"])
async def read_user_receipt(message: Message, state: FSMContext):
    deal = await get_deal(message.from_user.id)
    if deal:
        caption = (
            f"<b>Чек анкеты #{deal.id}</b>\n"
            f"<b>ID пользователя:</b> {message.from_user.id}\n\n"
            f"<b>❗️Подсказка</b>: <i>Ответный чек отправляйте ответным к этому сообщению</i>"
        )
        file_id = message.document.file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path
        ext = message.document.mime_type.split("/")[1]
        local_path = rf"media/receipt/users/{message.from_user.id}/{message.document.file_unique_id}.{ext}"
        await bot.download_file(file_path, local_path)
        document = read_local_file(local_path)
        if message.document.mime_type == "application/pdf":
            await bot.send_document(chat_id=config.main_group_id, document=document, caption=caption)
        elif message.document.mime_type in ["image/png", "image/jpeg"]:
            await bot.send_photo(chat_id=config.main_group_id, photo=document, caption=caption)
        await message.answer(text="Куда вам отправить?")
        return await state.set_state("receive")


@dp.message_handler(state="receive")
async def read_user_receive(message: Message, state: FSMContext):
    data = await state.get_data()
    deal_id = data.get("deal_id")
    message_page = (
        f"📍<b>ID заявки:</b> {deal_id}\n"
        F"👤<b>User ID:</b> {message.from_user.id}\n"
        F"🔗Username: @{message.from_user.username}\n"
        f"✉️<b>Куда отправить:</b> {message.text}"
    )
    await bot.send_message(chat_id=config.main_group_id, text=message_page)
    await message.answer(text="Ожидайте чек от администратора ...\n"
                         "Вы можете задать любой вопрос.")
    return await state.set_state("message")


@dp.message_handler(state="message")
async def chat(message: Message, state: FSMContext):
    data = await state.get_data()
    deal_id = data.get("deal_id")
    message_page = (
        f"📍<b>ID заявки:</b> {deal_id}\n"
        F"👤<b>User ID:</b> {message.from_user.id}\n"
        F"🔗Username: @{message.from_user.username}\n"
        f"✉️<b>Сообщение:</b> {message.text}"
    )
    await bot.send_message(chat_id=config.main_group_id, text=message_page)


async def create_deal(message: Message, state: FSMContext, user: User, send: str,
                      receive: str, method: str, amount: float, content: str, is_technical_task: bool):
    await state.finish()
    await User.objects.filter(user_id=message.from_user.id).update(is_chat=True)
    deal = await Deal.objects.create(user=user, send=send, receive=receive, method=method, amount=amount)
    await state.update_data(deal_id=deal.id)
    if is_technical_task:
        await TechnicalTask.objects.create(deal=deal, content=content)
        deal_page = (
            F"📌<b>Новая заявка #{deal.pk}</b>\n"
            F"👤<b>User ID:</b> {message.from_user.id}\n"
            F"🔗Username: @{message.from_user.username}\n"
            F"⚙️Обмен: {S_CURR_COUPLE.get(send)} ➜ {S_CURR_COUPLE.get(receive)}\n"
            F"💳Метод: {method}\n"
            F"📃Техническое задание: <code>{content}</code>"
        )
    else:
        deal_page = (
            F"📌<b>Новая заявка #{deal.pk}</b>\n"
            F"👤<b>User ID:</b> {message.from_user.id}\n"
            F"🔗Username: @{message.from_user.username}\n"
            F"⚙️Обмен: {S_CURR_COUPLE.get(send)} ➜ {S_CURR_COUPLE.get(receive)}\n"
            F"💳Метод: {method}\n"
            F"💰Сумма: {amount}"
        )
    try:
        await bot.send_message(config.main_group_id, deal_page)
        await message.answer(text="Заявка отправлена. Ожидайте ответа...\n"
                             "Вы можете задать любой вопрос.", reply_markup=PaymentKB.receipt())
        return await state.set_state("message")
    except BotKicked:
        logger.error(f"Bot kicked from chat: {config.main_group_id}")
        return await message.answer(text="При отправке возникла ошибка. Дождитесь её исправления ...")


async def finish_deal(message: Message, state: FSMContext, deal_id):
    await state.finish()
    user = await User.objects.get(user_id=message.from_user.id)
    await user.update(is_chat=False)
    deal = await Deal.objects.get(id=deal_id)
    await deal.update(finished=dt.utcnow())
    await bot.send_message(chat_id=config.main_group_id, text="Чек успешно отправлен.\n"
                                                              f"Заявка <b>#{deal.id}</b> успешно завершена!")
    return await bot.send_message(chat_id=message.from_user.id, text=f"Заявка #{deal.id} успешно завершена!",
                                  reply_markup=StartKB.start_keyboard())
