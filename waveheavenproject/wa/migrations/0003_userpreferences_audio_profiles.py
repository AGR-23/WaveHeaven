# Generated by Django 5.1.6 on 2025-03-14 05:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wa', '0002_alter_userpreferences_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='userpreferences',
            name='audio_profiles',
            field=models.JSONField(default=list),
        ),
    ]
