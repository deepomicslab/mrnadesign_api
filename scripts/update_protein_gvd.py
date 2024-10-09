import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Phage_api.settings")
import pandas as pd
from Phage_api import settings_local as local_settings
django.setup()
# ['Genbank', 'RefSeq', 'DDBJ', 'EMBL', 'tpg', 'PhagesDB', 'GPD', 'GVD', 'MGV', 'TemPhD']


def add_data():
    
    path='/home/platform/phage_db/phage_api/workspace/csv_data/Download/Annotated_protein_meta_data_v2/gvd_phage_annotated_protein_meta_data.tsv'
    proteincsv=pd.read_csv(path,sep='\t',low_memory=False)
    proinfodict={}
    for row in proteincsv.itertuples():
        proinfodict[row[7]]=[row[3],row[8],row[9]]
    from phage_protein.models import phage_protein_GVD
    proteins = phage_protein_GVD.objects.order_by('id')
    print("loading data")
    count=0
    for protein in proteins:
        
        if count%10000==0:
            print(count)
        count+=1
        protein.Function_prediction_source=proinfodict[protein.Protein_id][0]
        protein.Protein_product=proinfodict[protein.Protein_id][1]
        protein.Protein_function_classification=proinfodict[protein.Protein_id][2]
        path = local_settings.PROTEINSEQUENCE+'GVD/' + \
            protein.Phage_Acession_ID + '/' + protein.Protein_id + '.fasta'
        with open(path, 'r') as f:
            sequence = f.read()
            protein.prosequence=sequence
        protein.save()

if __name__ == "__main__":
    add_data()
    print('Done!')