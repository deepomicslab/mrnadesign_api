import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Phage_api.settings")

django.setup()


def add_data():
    from phage_protein.models import phage_protein_NCBI
    proteins = phage_protein_NCBI.objects.all()
