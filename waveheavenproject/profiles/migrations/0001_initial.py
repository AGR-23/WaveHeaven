# Generated by Django 5.1.6 on 2025-03-14 05:17

from django.db import migrations


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('wa', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SoundProfile',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('wa.userpreferences',),
        ),
    ]
