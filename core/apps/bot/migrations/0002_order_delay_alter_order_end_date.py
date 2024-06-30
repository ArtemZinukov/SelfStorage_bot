# Generated by Django 5.0.6 on 2024-06-30 21:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='delay',
            field=models.BooleanField(default=False, verbose_name='Просрочка'),
        ),
        migrations.AlterField(
            model_name='order',
            name='end_date',
            field=models.CharField(blank=True, max_length=20, verbose_name='Дата окончания'),
        ),
    ]
