# Generated by Django 5.1.7 on 2025-04-18 07:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_contactmessage'),
    ]

    operations = [
        migrations.AddField(
            model_name='contactmessage',
            name='is_read',
            field=models.BooleanField(default=False),
        ),
    ]
