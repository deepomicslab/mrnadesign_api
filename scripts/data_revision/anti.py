import django
import os
import pandas as pd
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Phage_api.settings")

django.setup()

# Protein_id = models.CharField(max_length=200, blank=True, null=True)
# Source = models.CharField(max_length=200, blank=True, null=True)
# Phage_Acession_ID = models.CharField(max_length=200, blank=True, null=True)
# dataset = models.CharField(max_length=200, blank=True, null=True)


def add_data():
    from phage_protein.models import phage_protein_anticrispr


    anticrispr=pd.read_csv('/home/platform/phage_db/phage_api/workspace/data_revision/AntiCRISPR.tsv',sep='\t')
    for row in anticrispr.itertuples():

        phage_protein_anticrispr.objects.create(
            Protein_id=row.Protein_ID, Source=row.Source, Phage_Acession_ID=row.Phage_ID, dataset=row.Phage_source)


if __name__ == "__main__":
    add_data()
