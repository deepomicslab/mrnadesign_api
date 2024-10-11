import django
import os,json
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mrnsdesign_api.settings")

django.setup()

def add_data():
    from tantigen_db.models import tantigen_db
    from mrnadesign_api import settings_local as local_settings
    import pandas as pd

    tantigendb_df = pd.read_csv(local_settings.MRNADESIGN_DATABASE + 'TAntigendb_se.csv').to_numpy()
    for l in tantigendb_df:
        tantigen_db.objects.create(
            agacc=l[0],
            antigen_name=l[1],
            full_name=l[2],
            synonym=l[3],
            uniprot_id=l[4],
            href1=l[5],
            ncbi_gene_id=l[6],
            href2=l[7],
            gene_card_id=l[8],
            href3=l[9],
            isoforms=l[10],
            rna_or_protein_expression_profile=l[11],
            href4=l[12],
            antigen_sequence=l[13],
        )

if __name__ == "__main__":
    add_data()