# Generated by Django 5.1.1 on 2024-09-17 04:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Jp7',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_no', models.CharField(max_length=32, verbose_name='品番')),
                ('item_name', models.CharField(max_length=256, verbose_name='製品名')),
                ('seal', models.CharField(blank=True, max_length=20, null=True, verbose_name='封印')),
                ('warning', models.TextField(blank=True, null=True, verbose_name='注意事項')),
            ],
            options={
                'verbose_name': 'JP7',
                'verbose_name_plural': 'JP7製品一覧',
                'db_table': 'jp7_items',
            },
        ),
        migrations.CreateModel(
            name='Jp7aInspectionItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='点検項目')),
                ('equipment_name', models.CharField(max_length=100, verbose_name='機器名')),
                ('inspection_frequency', models.CharField(max_length=50, verbose_name='点検頻度')),
                ('responsible_person', models.CharField(max_length=100, verbose_name='担当')),
            ],
            options={
                'verbose_name': 'JP7A保守点検',
                'verbose_name_plural': 'JP7A保守点検',
            },
        ),
        migrations.CreateModel(
            name='Jp7bInspectionItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='点検項目')),
                ('equipment_name', models.CharField(max_length=100, verbose_name='機器名')),
                ('inspection_frequency', models.CharField(max_length=50, verbose_name='点検頻度')),
                ('responsible_person', models.CharField(max_length=100, verbose_name='担当')),
            ],
            options={
                'verbose_name': 'JP7B保守点検',
                'verbose_name_plural': 'JP7B保守点検',
            },
        ),
        migrations.CreateModel(
            name='Jp7cInspectionItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='点検項目')),
                ('equipment_name', models.CharField(max_length=100, verbose_name='機器名')),
                ('inspection_frequency', models.CharField(max_length=50, verbose_name='点検頻度')),
                ('responsible_person', models.CharField(max_length=100, verbose_name='担当')),
            ],
            options={
                'verbose_name': 'JP7C保守点検',
                'verbose_name_plural': 'JP7C保守点検',
            },
        ),
        migrations.CreateModel(
            name='Jp7TroubleQuality',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('発生日', models.DateField()),
                ('トラブル名', models.CharField(max_length=256)),
                ('トラブル内容', models.TextField(blank=True, null=True)),
                ('対策', models.TextField(blank=True, null=True)),
                ('分類', models.CharField(blank=True, max_length=16, null=True)),
            ],
            options={
                'verbose_name': 'JP7品質トラブル',
                'verbose_name_plural': 'JP7品質トラブル',
                'db_table': 'jp7_trouble_quality',
            },
        ),
        migrations.CreateModel(
            name='Jp7TroubleSafety',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('発生日', models.DateField()),
                ('トラブル名', models.CharField(max_length=256)),
                ('トラブル内容', models.TextField(blank=True, null=True)),
                ('対策', models.TextField(blank=True, null=True)),
                ('分類', models.CharField(blank=True, max_length=16, null=True)),
            ],
            options={
                'verbose_name': 'JP7安全トラブル',
                'verbose_name_plural': 'JP7安全トラブル',
                'db_table': 'jp7_trouble_safety',
            },
        ),
        migrations.CreateModel(
            name='Jp7aInspectionRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('inspection_date', models.DateField()),
                ('result', models.BooleanField(default=False)),
                ('manager_confirmation_date', models.DateTimeField(blank=True, null=True)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jp7.jp7ainspectionitem')),
            ],
            options={
                'verbose_name': 'JP7A保守点検記録',
                'verbose_name_plural': 'JP7A保守点検記録',
            },
        ),
        migrations.CreateModel(
            name='Jp7bInspectionRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('inspection_date', models.DateField()),
                ('result', models.BooleanField(default=False)),
                ('manager_confirmation_date', models.DateTimeField(blank=True, null=True)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jp7.jp7binspectionitem')),
            ],
            options={
                'verbose_name': 'JP7B保守点検記録',
                'verbose_name_plural': 'JP7B保守点検記録',
            },
        ),
        migrations.CreateModel(
            name='Jp7cInspectionRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('inspection_date', models.DateField()),
                ('result', models.BooleanField(default=False)),
                ('manager_confirmation_date', models.DateTimeField(blank=True, null=True)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jp7.jp7cinspectionitem')),
            ],
            options={
                'verbose_name': 'JP7C保守点検記録',
                'verbose_name_plural': 'JP7C保守点検記録',
            },
        ),
        migrations.CreateModel(
            name='Jp7PDF',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='PDF名')),
                ('file', models.FileField(upload_to='jp7_pdfs/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('jp7', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pdf_files', to='jp7.jp7')),
            ],
            options={
                'verbose_name': 'JP7 PDF',
                'verbose_name_plural': 'JP7 PDFs',
                'db_table': 'jp7_pdfs',
            },
        ),
    ]
