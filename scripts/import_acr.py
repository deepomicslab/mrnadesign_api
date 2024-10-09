import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Phage_api.settings")

django.setup()

# Protein_id = models.CharField(max_length=200, blank=True, null=True)
# Source = models.CharField(max_length=200, blank=True, null=True)
# Phage_Acession_ID = models.CharField(max_length=200, blank=True, null=True)
# dataset = models.CharField(max_length=200, blank=True, null=True)


def add_data():
    from phage_protein.models import phage_protein_anticrispr

    with open('/home/platform/phage_db/phage_api/workspace/csv_data/acr_result.csv', 'r') as f:
        lines = f.readlines()

    for line in lines:
        l = line.strip().split("\t")
        phage_protein_anticrispr.objects.create(
            Protein_id=l[0], Source=l[1], Phage_Acession_ID=l[2], dataset=l[3])


if __name__ == "__main__":
    add_data()
