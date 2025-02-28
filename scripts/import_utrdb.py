import django
import os,json
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mrnsdesign_api.settings")

django.setup()

def add_data():
    from utrdb.models import utrdb
    from mrnadesign_api import settings_local as local_settings
    import pandas as pd
    
    arr = []
    with open(local_settings.MRNADESIGN_DATABASE + 'utrdb2/Pediculus_humanus.PhumU2.54.utrs', 'r') as file:
        L = file.readlines()
    for l in L:
        if l.startswith('#'):
            continue
        if l.startswith('>|'):
            arr.append([i.replace('\n', '') for i in l[2:].split('|')])
            arr[-1].append('')
        else:
            arr[-1][-1] += l.replace('\n', '')

    for l in arr:
        utrdb.objects.create(
            utr_type=l[0],
            transcript_id=l[1],
            gene_id=l[2],
            chr_start_end_strand=l[3],
            sequence=l[4],
        )

if __name__ == "__main__":
    add_data()