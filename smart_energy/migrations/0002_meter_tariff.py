# Generated by Django 2.2.3 on 2019-07-20 11:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('smart_energy', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='meter',
            name='tariff',
            field=models.SmallIntegerField(default=1),
        ),
    ]
