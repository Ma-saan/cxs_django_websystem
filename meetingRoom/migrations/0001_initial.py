# Generated by Django 5.1.1 on 2024-09-13 02:02

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('event_name', models.CharField(max_length=20)),
                ('person', models.CharField(max_length=20)),
                ('room_name', models.CharField(max_length=12)),
            ],
        ),
    ]
