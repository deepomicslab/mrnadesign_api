import django
import os
import pandas as pd
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Phage_api.settings")

django.setup()

#Phage_ID	Length	GC_content	Taxonomy	Completeness	Host	Lifestyle	Cluster	Subcluster	Phage_source	reference
def add_data():
    from phage.models import phage
    from datasets.models import datasets


    phagedf = pd.read_csv('/home/platform/phage_db/phage_api/workspace/data_revision/phage.tsv', sep='\t')
    for row in phagedf.itertuples():
        ds = datasets.objects.get(name=row.Phage_source)
        phage.objects.create(Acession_ID=row.Phage_ID, Data_Sets=ds, length=row.Length, gc_content=row.GC_content, 
        host=row.Host, completeness=row.Completeness, taxonomy=row.Taxonomy, cluster=row.Cluster, subcluster=row.Subcluster,
        reference=row.reference)





if __name__ == "__main__":
    add_data()