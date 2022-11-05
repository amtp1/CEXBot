from models.models import User, Deal


async def check_order(message, state):
    await state.finish()
    user = await User.objects.get(user_id=message.from_user.id)
    deals = list(await Deal.objects.filter(user=user).all())
    if deals:
        deal = deals[-1]
        if not deal.finished:
            if not deal.is_cancel:
                await deal.update(is_cancel=True)
                return await message.answer(text="Предыдущая заявка была отменена!")
