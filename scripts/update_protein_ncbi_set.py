import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Phage_api.settings")

django.setup()


def update_data():
    dataset=['Genbank', 'RefSeq', 'DDBJ', 'EMBL', 'Genbank', 'PhagesDB', 'GPD', 'GVD', 'MGV', 'TemPhD']
    from phage_protein.models import phage_protein_NCBI
    proteins = phage_protein_NCBI.objects.order_by('id')
    print("loading data")
    count=0
    for protein in proteins:
        if count%1000==0:
            print(count)
        count+=1
        protein.Function_prediction_source=dataset[int(protein.dataset)-1]
        protein.save()
        #print(protein.dataset)

if __name__ == "__main__":
    update_data()
    print('Done!')