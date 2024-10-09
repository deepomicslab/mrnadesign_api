import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Phage_api.settings")
import pandas as pd
from Phage_api import settings_local as local_settings
django.setup()


def add_data():
    baseurl = '/home/platform/phage_db/phage_data/data/csv_data/Download/Annotated_protein_meta_data_v2/'
    dataset = ['gov2_phage_annotated_protein_meta_data.tsv', 
            'igvd_phage_annotated_protein_meta_data.tsv', 
            'stv_phage_annotated_protein_meta_data.tsv', 
            'chvd_phage_annotated_protein_meta_data.tsv',
            'img_vr_phage_annotated_protein_meta_data.tsv']

    print(dataset[4])
    phage_protein = pd.read_csv(baseurl+dataset[4], sep='\t')
    proteindict_df = phage_protein.set_index('Protein_ID')['Function_Prediction_source'].to_dict()
    from phage_protein.models import phage_protein_IMG_VR,phage_protein_CHVD,phage_protein_IGVD,phage_protein_GOV2,phage_protein_STV
    from Bio import SeqIO
    
    fatsapath='/home/platform/phage_db/phage_data/data/phage_sequence/proteins/IMG_VR.fasta'

    prodict={}
    with open(fatsapath, 'r') as fasfile:
        for record in SeqIO.parse(fasfile, 'fasta'):
            prodict[record.id]=str(record.seq)
 
    print("loading data")
    count=0
    proteins = phage_protein_IMG_VR.objects.order_by('id')
    for protein in proteins:
        
        if count%10000==0:
            print(count)
        count+=1
        seq=str(prodict[protein.Protein_id])
        nseq=''
        while len(seq) > 70:
            nseq=nseq+seq[:70] + "\n"
            seq = seq[70:]
        nseq=nseq+seq + "\n"
        seq='>'+str(protein.Protein_id)+'\n'+nseq+'\n'
        protein.prosequence=seq
        protein.Function_prediction_source=proteindict_df[protein.Protein_id]
        protein.save()

if __name__ == "__main__":
    add_data()
    print('Done!')