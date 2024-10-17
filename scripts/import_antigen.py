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
            db_info=l[2],
            sequence=l[3],
            antigen_type=l[4],
            model_structure=l[5],
            href2=l[6],
            surface_access=l[7],
            href3=l[8],
            protein_class=l[9],
            database_reference1=l[10],
            href4=l[11],
            database_reference2=l[12],
            href5=l[13],
            database_reference3=l[14],
            href6=l[15],
            source_organism=l[16],
            href7=l[17],
            literature_reference=l[18],
            href8=l[19],
        )


if __name__ == "__main__":
    add_data()