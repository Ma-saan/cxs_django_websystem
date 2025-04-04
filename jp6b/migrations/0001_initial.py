# Generated by Django 5.1.5 on 2025-02-13 05:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Jp6b',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_no', models.CharField(max_length=32, verbose_name='品番')),
                ('item_name', models.CharField(max_length=256, verbose_name='製品名')),
                ('specific', models.CharField(blank=True, max_length=20, null=True, verbose_name='特殊')),
                ('bottle', models.CharField(blank=True, max_length=20, null=True, verbose_name='ボトル')),
                ('warning', models.TextField(blank=True, null=True, verbose_name='注意事項')),
                ('kind_no', models.CharField(blank=True, max_length=20, null=True, verbose_name='品種番号')),
            ],
            options={
                'verbose_name': 'JP6B',
                'verbose_name_plural': 'JP6B製品一覧',
                'db_table': 'jp6b_items',
            },
        ),
        migrations.CreateModel(
            name='Jp6bInspectionItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='点検項目')),
                ('equipment_name', models.CharField(max_length=100, verbose_name='機器名')),
                ('inspection_frequency', models.CharField(max_length=50, verbose_name='点検頻度')),
                ('responsible_person', models.CharField(max_length=100, verbose_name='担当')),
            ],
            options={
                'verbose_name': 'JP6B保守点検',
                'verbose_name_plural': 'JP6B保守点検',
            },
        ),
        migrations.CreateModel(
            name='Jp6bTroubleQuality',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('発生日', models.DateField()),
                ('トラブル名', models.CharField(max_length=256)),
                ('トラブル内容', models.TextField(blank=True, null=True)),
                ('対策', models.TextField(blank=True, null=True)),
                ('分類', models.CharField(blank=True, max_length=16, null=True)),
            ],
            options={
                'verbose_name': 'JP6B品質トラブル',
                'verbose_name_plural': 'JP6B品質トラブル',
                'db_table': 'jp6b_trouble_quality',
            },
        ),
        migrations.CreateModel(
            name='Jp6bTroubleSafety',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('発生日', models.DateField()),
                ('トラブル名', models.CharField(max_length=256)),
                ('トラブル内容', models.TextField(blank=True, null=True)),
                ('対策', models.TextField(blank=True, null=True)),
                ('分類', models.CharField(blank=True, max_length=16, null=True)),
            ],
            options={
                'verbose_name': 'JP6B安全トラブル',
                'verbose_name_plural': 'JP6B安全トラブル',
                'db_table': 'jp6b_trouble_safety',
            },
        ),
        migrations.CreateModel(
            name='Jp6bInspectionRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('inspection_date', models.DateField()),
                ('result', models.BooleanField(default=False)),
                ('manager_confirmation_date', models.DateTimeField(blank=True, null=True)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jp6b.jp6binspectionitem')),
            ],
            options={
                'verbose_name': 'JP6B保守点検記録',
                'verbose_name_plural': 'JP6B保守点検記録',
            },
        ),
        migrations.CreateModel(
            name='Jp6bPDF',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='PDF名')),
                ('file', models.FileField(upload_to='jp6b_pdfs/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('jp6b', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pdf_files', to='jp6b.jp6b')),
            ],
            options={
                'verbose_name': 'JP6b PDF',
                'verbose_name_plural': 'JP6b PDFs',
                'db_table': 'jp6b_pdfs',
            },
        ),
    ]
