import django
import os
import pandas as pd
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Phage_api.settings")

django.setup()
#Phage_ID	Host	Source	Host_species	Host_genus	Host_family	Host_order	Host_class	Host_phylum	id
def add_data():
    from phage.models import phage
    from phage_hosts.models import phage_hosts
    path='/home/platform/phage_db/phage_api/workspace/data_revision/host.csv'
    phage_host_df = pd.read_csv(path, sep='\t')
    print('load data')
    for row in phage_host_df.itertuples():
        dp = phage.objects.get(id=int(row.id))
        phage_hosts.objects.create(
            accesion_id=row.Phage_ID, host=row.Host, host_source=row.Source, Species=row.Host_species, 
            Genus=row.Host_genus, Family=row.Host_family, Order=row.Host_order, Class=row.Host_class, Phylum=row.Host_phylum, phage=dp)

add_data()