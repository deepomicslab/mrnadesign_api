import django
import os
import pandas as pd
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Phage_api.settings")

django.setup()

def add_data():
    from phage.models import phage
    from phage_lifestyle.models import phage_lifestyle
    path='/home/platform/phage_db/phage_api/workspace/data_revision/lifestyle.csv'
    phage_lifestyle_df = pd.read_csv(path, sep='\t')
    print('load data')
    for row in phage_lifestyle_df.itertuples():
        dp = phage.objects.get(id=int(row.id))
        phage_lifestyle.objects.create(accesion_id=row.Phage_ID, lifestyle=row.Lifestyle, phage=dp)

add_data()