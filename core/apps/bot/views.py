from django.shortcuts import render
from core.apps.bot.models import Order


def image_page(request):
    data = Order.objects.all()
    return render(request, 'image_page.html', {'data': data})

# Create your views here.

