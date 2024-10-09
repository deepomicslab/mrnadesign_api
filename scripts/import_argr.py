import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Phage_api.settings")

django.setup()

    # Protein_id = models.CharField(max_length=200, blank=True, null=True)
    # Aligned_Protein_in_VFDB   = models.CharField(max_length=200, blank=True, null=True)
    # Phage_Acession_ID = models.CharField(max_length=200, blank=True, null=True)
    # dataset = models.CharField(max_length=200, blank=True, null=True)


def add_data():
    from phage_protein.models import phage_antimicrobial_resistance_gene

    with open('/home/platform/phage_db/phage_api/workspace/rawd_data/Virulent_factor_Antimicrobial_resistance_gene_V2/all_phage_result/all_antimicrobial_resistance_gene_results.tsv', 'r') as f:
        lines = f.readlines()

    for line in lines:
        l = line.strip().split("\t")
        phage_antimicrobial_resistance_gene.objects.create(
            Protein_id=l[0], Aligned_Protein_in_CARD=l[1], Phage_Acession_ID=l[2], dataset=l[3])


if __name__ == "__main__":
    add_data()