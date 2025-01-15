import django
import os,json
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mrnadesign_api.settings")

django.setup()

def add_data():
    from mirtarbase_db.models import mirtarbase_db
    from mrnadesign_api import settings_local as local_settings
    import pandas as pd

    mirtarbase_db_df = pd.read_csv(local_settings.MRNADESIGN_DATABASE + 'mirtarbase/MicroRNA_Target_Sites_Strong_Evidence.csv').to_numpy()
    for l in mirtarbase_db_df:
        mirtarbase_db.objects.create(
            mirtarbase_id=l[0],
            mirna=l[1],
            species_mirna=l[2],
            target_gene=l[3],
            target_gene_entrez_gene_id=l[4],
            species_target_gene=l[5],
            target_site=l[6],
            experiments=l[7],
            support_type=l[8],
            references_pmid=l[9],
        )


if __name__ == "__main__":
    add_data()