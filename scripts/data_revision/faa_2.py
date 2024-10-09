import pandas as pd
names=['Phage_ID','Protein_source','Function_Prediction_source','Start','Stop','Strand','Protein_ID','Product','Protein_classification','Molecular_weight','Aromaticity','Instability_index','Isoelectric_point','Helix_fraction','Turn_fraction','Sheet_fraction','Reduced_coefficient','Oxidized_coefficient','Phage_source']
phage_protein = pd.read_csv('/home/platform/phage_db/phage_api/workspace/data_revision/protein/phage_protein_info.tsv', sep='\t',names=names)
proteindict_df = phage_protein.set_index('Protein_ID')['Phage_ID'].to_dict()


from Bio import SeqIO
fatsapath='/home/platform/phage_db/phage_api/workspace/data_revision/protein/02.IGVD/gene.faa'

print('start')
with open(fatsapath, 'r') as fasfile:
    for record in SeqIO.parse(fasfile, 'fasta'):
        protein_id=record.id.split(' # ')[0]
        phageid=proteindict_df[protein_id]
        with open('/home/platform/phage_db/phage_data/data/phage_sequence/phage_faa/IGVD/'+phageid+'.faa','a') as f:
                    f.write('>'+record.id+'\n')
                    seq=str(record.seq)
                    while len(seq) > 70:
                        f.write(seq[:70] + "\n")
                        seq = seq[70:]
                    f.write(seq + "\n")
                    f.close()
