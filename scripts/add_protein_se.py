import django
import os
from Phage_api import settings_local as local_settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Phage_api.settings")

django.setup()


def update_data():
    datasetlist = ['Genbank', 'RefSeq', 'DDBJ', 'EMBL', 'tpg']
    
    from phage_protein.models import phage_protein_NCBI
    proteins = phage_protein_NCBI.objects.order_by('id')
    print("loading data")
    count=0
    for protein in proteins:
        count+=1
        if count%100000==0:
            print(count)
        dataset = datasetlist[int(protein.dataset)-1]
        path = local_settings.PROTEINSEQUENCE+str(dataset) + "/" +\
            protein.Phage_Acession_ID + '/' + protein.Protein_id + '.fasta'
        with open(path, 'r') as f:
            sequence = f.read()
            protein.prosequence=sequence
            protein.save()
        #print(protein.dataset)

if __name__ == "__main__":
    update_data()
    print('Done!')