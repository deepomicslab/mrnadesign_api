# Generated by Django 4.2.1 on 2025-01-22 09:57

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='rebase_data',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('accession_number', models.CharField(blank=True, max_length=200, null=True)),
                ('recognition_seq_w_cleavage_site', models.CharField(blank=True, max_length=200, null=True)),
                ('recognition_site', models.CharField(blank=True, max_length=200, null=True)),
                ('enzyme_name_list', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=200, null=True), size=None)),
                ('enzyme_type', models.CharField(blank=True, max_length=200, null=True)),
                ('suppliers', models.TextField(blank=True, null=True)),
                ('prototype', models.CharField(blank=True, max_length=200, null=True)),
            ],
            options={
                'verbose_name': 'rebase_data',
                'verbose_name_plural': 'rebase_data',
                'db_table': 'rebase_data',
            },
        ),
        migrations.CreateModel(
            name='rebase_enzyme_link',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('enzyme_name', models.CharField(blank=True, max_length=200, null=True)),
                ('enzyme_page', models.CharField(blank=True, max_length=200, null=True)),
            ],
            options={
                'verbose_name': 'rebase_enzyme_link',
                'verbose_name_plural': 'rebase_enzyme_link',
                'db_table': 'rebase_enzyme_link',
            },
        ),
    ]