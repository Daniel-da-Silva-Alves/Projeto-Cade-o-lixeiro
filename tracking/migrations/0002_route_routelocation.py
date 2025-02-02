# Generated by Django 5.1.3 on 2024-11-17 00:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracking', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Route',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('route_id', models.CharField(max_length=50, unique=True)),
                ('start_address', models.CharField(max_length=255)),
                ('end_address', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('truck', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tracking.truck')),
            ],
        ),
        migrations.CreateModel(
            name='RouteLocation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('address', models.CharField(max_length=255)),
                ('order', models.IntegerField()),
                ('route', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='locations', to='tracking.route')),
            ],
        ),
    ]
