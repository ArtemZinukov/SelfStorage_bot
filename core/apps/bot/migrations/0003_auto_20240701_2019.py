# Generated by Django 2.2.24 on 2024-07-01 17:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0002_order_delay_alter_order_end_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='referrals',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
