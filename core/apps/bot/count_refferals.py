from django.db.models import F
from core.apps.bot.models import Referrals


def count_referrals(link):
    try:
        referral = Referrals.objects.get(link=link)
        referral.count = F('count') + 1
        referral.save()
    except Referrals.DoesNotExist:
        Referrals.objects.create(link=link, count=1)


def count_referrals_message(link):
    return Referrals.objects.get(link=link).count
