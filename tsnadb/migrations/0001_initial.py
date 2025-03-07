# Generated by Django 4.2.1 on 2025-01-22 08:13

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='tsnadb_neoantigen',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(blank=True, max_length=200, null=True)),
                ('tissue', models.CharField(blank=True, max_length=200, null=True)),
                ('mutation', models.CharField(blank=True, max_length=200, null=True)),
                ('hla', models.CharField(blank=True, max_length=200, null=True)),
                ('peptide', models.CharField(blank=True, max_length=200, null=True)),
                ('deep_bind', models.FloatField(blank=True, null=True)),
                ('deep_imm', models.FloatField(blank=True, null=True)),
                ('nhcf_rank_percent', models.FloatField(blank=True, null=True)),
                ('net4_aff_nm', models.FloatField(blank=True, null=True)),
                ('net4_aff_percent', models.FloatField(blank=True, null=True)),
                ('tpm', models.FloatField(blank=True, null=True)),
                ('frequency_in_the_tissue', models.CharField(blank=True, max_length=200, null=True)),
                ('frequency_in_all_samples', models.CharField(blank=True, max_length=200, null=True)),
            ],
            options={
                'verbose_name': 'tsnadb_neoantigen',
                'verbose_name_plural': 'tsnadb_neoantigen',
                'db_table': 'tsnadb_neoantigen',
            },
        ),
        migrations.CreateModel(
            name='tsnadb_validated',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.CharField(blank=True, max_length=200, null=True)),
                ('patient_id', models.CharField(blank=True, max_length=200, null=True)),
                ('tumor_type', models.CharField(blank=True, max_length=200, null=True)),
                ('tumor_type_detaile', models.CharField(blank=True, max_length=200, null=True)),
                ('mutation_type', models.CharField(blank=True, max_length=200, null=True)),
                ('gene', models.CharField(blank=True, max_length=200, null=True)),
                ('mutation', models.CharField(blank=True, max_length=200, null=True)),
                ('position', models.CharField(blank=True, max_length=200, null=True)),
                ('mutant_peptide', models.CharField(blank=True, max_length=200, null=True)),
                ('hla', models.CharField(blank=True, max_length=200, null=True)),
                ('pubmed_id', models.CharField(blank=True, max_length=200, null=True)),
                ('reference_name', models.CharField(blank=True, max_length=500, null=True)),
                ('journal', models.CharField(blank=True, max_length=200, null=True)),
                ('year', models.IntegerField(blank=True, null=True)),
                ('doi', models.CharField(blank=True, max_length=500, null=True)),
            ],
            options={
                'verbose_name': 'tsnadb_validated',
                'verbose_name_plural': 'tsnadb_validated',
                'db_table': 'tsnadb_validated',
            },
        ),
    ]
