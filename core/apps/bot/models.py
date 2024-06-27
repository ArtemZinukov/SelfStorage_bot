from django.db import models


class Order(models.Model):
    client_name = models.CharField(verbose_name="Имя клиента", max_length=200, blank=True)
    address = models.CharField(verbose_name='Адрес', max_length=200, blank=True)
    phone_number = models.CharField(verbose_name='Номер телефона', max_length=12, blank=True)
    date = models.CharField(verbose_name='Дата', max_length=20, blank=True)
    email = models.CharField(verbose_name='E-mail', max_length=30, blank=True)





