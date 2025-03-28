# Generated by Django 5.1.5 on 2025-03-27 05:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ProductSchedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('production_date', models.DateField(verbose_name='生産日')),
                ('product_number', models.CharField(max_length=50, verbose_name='品番')),
                ('product_name', models.CharField(max_length=255, verbose_name='製品名')),
                ('production_quantity', models.IntegerField(default=0, verbose_name='生産数')),
                ('grid_row', models.IntegerField(default=0, verbose_name='縦位置')),
                ('grid_column', models.IntegerField(default=0, verbose_name='横位置')),
                ('display_color', models.CharField(default='#FFFFFF', max_length=20, verbose_name='表示色')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='備考')),
                ('last_updated', models.DateTimeField(auto_now=True, verbose_name='最終更新日時')),
            ],
            options={
                'verbose_name': '生産予定',
                'verbose_name_plural': '生産予定',
            },
        ),
        migrations.CreateModel(
            name='WorkCenter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='ワークセンター名')),
                ('display_name', models.CharField(max_length=50, verbose_name='表示名')),
                ('color', models.CharField(default='#FFFFFF', max_length=20, verbose_name='表示色')),
                ('order', models.IntegerField(default=0, verbose_name='表示順')),
            ],
            options={
                'verbose_name': 'ワークセンター',
                'verbose_name_plural': 'ワークセンター',
            },
        ),
        migrations.CreateModel(
            name='ScheduleAttribute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attribute_type', models.CharField(max_length=50, verbose_name='属性タイプ')),
                ('value', models.CharField(blank=True, max_length=255, null=True, verbose_name='値')),
                ('schedule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attributes', to='schedule_manager.productschedule')),
            ],
            options={
                'verbose_name': '予定属性',
                'verbose_name_plural': '予定属性',
            },
        ),
        migrations.AddField(
            model_name='productschedule',
            name='work_center',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='schedule_manager.workcenter', verbose_name='ワークセンター'),
        ),
        migrations.AlterUniqueTogether(
            name='productschedule',
            unique_together={('production_date', 'work_center', 'product_number')},
        ),
    ]
