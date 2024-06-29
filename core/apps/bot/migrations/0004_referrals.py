# Generated by Django 2.2.24 on 2024-06-29 12:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0003_order_volume'),
    ]

    operations = [
        migrations.CreateModel(
            name='Referrals',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('link', models.CharField(max_length=200, unique=True, verbose_name='Откуда пришли')),
                ('count', models.IntegerField(default=0, verbose_name='Количество переходов')),
            ],
        ),
    ]
