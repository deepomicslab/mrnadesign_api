import django
import os,json
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mrnsdesign_api.settings")

django.setup()

def add_data():
    from tantigen_rna_seq.models import tantigen_rna_seq
    from mrnadesign_api import settings_local as local_settings
    import pandas as pd

    tantigendb_df = pd.read_csv(local_settings.MRNADESIGN_DATABASE + 'Tantigen_rna_seq.csv').to_numpy()
    for l in tantigendb_df:
        tantigen_rna_seq.objects.create(
            agacc=l[0],
            antigen_name=l[1],
            seq_5=l[2],
            cds=l[3],
            seq_3=l[4],
        )

if __name__ == "__main__":
    add_data()