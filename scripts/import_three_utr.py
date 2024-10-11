import django
import os,json
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mrnsdesign_api.settings")

django.setup()

def add_data():
    from three_utr.models import three_utr
    from mrnadesign_api import settings_local as local_settings
    import pandas as pd

    three_utr_df = pd.read_csv(local_settings.MRNADESIGN_DATABASE + 'Complete_3_UTR_ARE_Data/Complete_3_UTR_Data.csv').to_numpy()
    for l in three_utr_df:
        three_utr.objects.create(
            gene_name=l[0],
            ensembl_gene_id=l[1],
            ensembl_transcript_id=l[2],
            description=l[3],
            start_position=l[4],
            end_position = l[5],
            pattern = l[6],
            cluster = l[7],
            chromosome = l[8],
            aliases = l[9],
        )

if __name__ == "__main__":
    add_data()