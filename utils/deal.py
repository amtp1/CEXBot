from models.models import Deal, User


async def get_deal(user_id: int) -> Deal:
    user = await User.objects.get(user_id=user_id)
    deals = await Deal.objects.filter(user=user, is_cancel=False, finished=None).all()
    deal = list(deals)[-1]
    return deal
