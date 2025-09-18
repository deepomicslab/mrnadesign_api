import django
import os,json
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mrnsdesign_api.settings")
from . import utils
from pathlib import Path

django.setup()

def add_data():
    from tcrabpairing.models import tcrabpairing
    from mrnadesign_api import settings_local as local_settings
    import pandas as pd

    fpath = local_settings.MRNADESIGN_DATABASE / 'tcrabpairing' / 'GSM6063507_230093_primary_focus_filtered_contig_annotations.csv'
    \
    source = fpath.name.split('.')[0]
    
    tcrfile = pd.read_csv(fpath)
    sorted_file = utils.process_10x_dataset(tcrfile)
    to_create = []
    for i, row in sorted_file.iterrows():
        cell_dict = row.to_dict()
        cell_dict['source'] = source
        to_create.append(tcrabpairing(**cell_dict))

    tcrabpairing.objects.bulk_create(to_create, ignore_conflicts=True)

if __name__ == "__main__":
    add_data()