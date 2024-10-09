import django
import os
import pandas as pd
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Phage_api.settings")

django.setup()
def add_data():
    from phage.models import phage
    phage_df = pd.read_csv('/home/platform/phage_db/phage_api/workspace/data_revision/rep_red_phage.tsv', sep='\t')
    print('load data')
    for row in phage_df.itertuples():
        dp = phage.objects.get(id=int(row.id))
        dp.is_rep = row.is_rep
        dp.is_redundant = row.is_redundant
        dp.save()

add_data()