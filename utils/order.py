from models.models import User, Deal
from objects.globals import bot, config


async def check_order(message, state):
    await state.finish()
    user = await User.objects.get(user_id=message.from_user.id)
    deals = list(await Deal.objects.filter(user=user).all())
    if deals:
        deal = deals[-1]
        if not deal.finished:
            if not deal.is_cancel:
                await deal.update(is_cancel=True)
                await bot.send_message(chat_id=config.main_group_id, text=f"<b>Заявка #{deal.pk}</b> была отменена!")
                return await message.answer(text=f"Предыдущая <b>заявка #{deal.pk}</b> была отменена!")
