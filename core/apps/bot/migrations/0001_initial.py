# Generated by Django 5.0.6 on 2024-06-29 22:21

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('client_name', models.CharField(blank=True, max_length=200, verbose_name='Имя клиента')),
                ('address', models.CharField(blank=True, max_length=200, verbose_name='Адрес')),
                ('phone_number', models.CharField(blank=True, max_length=12, verbose_name='Номер телефона')),
                ('date', models.CharField(blank=True, max_length=20, verbose_name='Дата')),
                ('end_date', models.CharField(blank=True, max_length=20, verbose_name='Дата')),
                ('email', models.CharField(blank=True, max_length=30, verbose_name='E-mail')),
                ('volume', models.CharField(blank=True, max_length=30, verbose_name='Объем вещей')),
                ('qr_code', models.ImageField(blank=True, upload_to='qr_codes')),
                ('delivery', models.BooleanField(default=False, verbose_name='Доставка')),
            ],
            options={
                'verbose_name': 'Заказ',
                'verbose_name_plural': 'Заказы',
            },
        ),
        migrations.CreateModel(
            name='Referrals',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('link', models.CharField(max_length=200, unique=True, verbose_name='Откуда пришли')),
                ('count', models.IntegerField(default=0, verbose_name='Количество переходов')),
            ],
            options={
                'verbose_name': 'Реферал',
                'verbose_name_plural': 'Рефералы',
            },
        ),
    ]
