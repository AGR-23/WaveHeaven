# Generated by Django 5.1.6 on 2025-03-17 21:53

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wa', '0005_userpreferences_birthday'),
    ]

    operations = [
        migrations.AddField(
            model_name='exposurereport',
            name='date',
            field=models.DateField(default=datetime.date.today),
        ),
    ]
