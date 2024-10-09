import django
import os
import pandas as pd
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Phage_api.settings")

django.setup()

    # Protein_id = models.CharField(max_length=200, blank=True, null=True)
    # Aligned_Protein_in_VFDB   = models.CharField(max_length=200, blank=True, null=True)
    # Phage_Acession_ID = models.CharField(max_length=200, blank=True, null=True)
    # dataset = models.CharField(max_length=200, blank=True, null=True)


def add_data():
    from phage_protein.models import phage_virulent_factor


    ar=pd.read_csv('/home/platform/phage_db/phage_api/workspace/data_revision/virulence_factor/virulence_factor.tsv',sep='\t')
    for row in ar.itertuples():
        phage_virulent_factor.objects.create(
            Protein_id=row.Protein_id, Aligned_Protein_in_VFDB=row.Aligned_Protein_in_VFDB, Phage_Acession_ID=row.Phage_id, dataset=row.Phage_Source)

if __name__ == "__main__":
    add_data()

