# Generated by Django 5.1.3 on 2024-11-25 04:35

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracking', '0004_truck_truck_neighborhood'),
    ]

    operations = [
        migrations.AddField(
            model_name='routelocation',
            name='passage_time',
            field=models.TimeField(default=django.utils.timezone.now),
        ),
    ]
