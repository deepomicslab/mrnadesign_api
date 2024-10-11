import django
import os,json
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mrnadesign_api.settings")

django.setup()

def add_data():
    from antigen.models import antigen
    from mrnadesign_api import settings_local as local_settings
    import pandas as pd

    antigen_df = pd.read_csv(local_settings.MRNADESIGN_DATABASE + 'Antigen_se.csv').to_numpy()
    for l in antigen_df:
        antigen.objects.create(
            antigen_name=l[0],
            antigen_aequence=l[1],
            sequence=l[2],
            antigen_type=l[3],
            model_structure=l[4],
            href2=l[5],
            surface_access=l[6],
            href3=l[7],
            protein_class=l[8],
            database_reference1=l[9],
            href4=l[10],
            database_reference2=l[11],
            href5=l[12],
            database_reference3=l[13],
            href6=l[14],
            source_organism=l[15],
            href7=l[16],
            literature_reference=l[17],
            href8=l[18],
        )


if __name__ == "__main__":
    add_data()