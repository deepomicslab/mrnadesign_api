import django
import os
import json
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mrnadesign_api.settings")

django.setup()


def add_data():
    from gtrnadb.models import gtrnadb_genome, gtrnadb_data
    from mrnadesign_api import settings_local as local_settings
    import pandas as pd
    import numpy as np

    gtrnadb_genome_df = pd.read_csv(
        local_settings.MRNADESIGN_DATABASE + 'gtrnadb/gtrnadb_url.tsv', sep='\t').fillna('').to_numpy()

    for l in gtrnadb_genome_df:
        gtrnadb_genome.objects.create(
            domain=l[0],
            genome=l[1],
            genomeid=l[2],
            gtrnadb_url=l[3],
            tax_id=str(int(l[4])),
            genbank_common_name=l[5],
            scientific_name=l[6],
        )

    gtrnadb_data_df = pd.read_csv(
        local_settings.MRNADESIGN_DATABASE + 'gtrnadb/gtrnadb_data.csv').to_numpy()

    for l in gtrnadb_data_df:
        gtrnadb_data.objects.create(
            genomeid=l[2],
            gtrnadb_id=l[3],
            trna_scan_id=l[4],
            trna_scan_id_code=l[5],
            chr=l[6],
            start=str(int(l[7])),
            end=str(int(l[8])),
            strand=l[9],
            isotype=l[10],
            anticodon=l[11],
            intron_count=int(l[12]),
            mismatches=int(l[13]),
            score=float(l[14]),
            pseudogene=int(l[15]),
            ids=l[16],
            length=int(l[17]),
            len_mature=int(l[18]) if not np.isnan(l[18]) else None,
        )


if __name__ == "__main__":
    add_data()
