import django
import os
import pandas as pd
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Phage_api.settings")

django.setup()

# Pandas(Index=0, Phage_ID='SRS101376_a1_ct99314_vs01', Protein_source='prodigal', Function_Prediction_source='eggNOG-mapper', 
# Start=319, Stop=1062, Strand='-', Protein_ID='SRS101376_a1_ct99314_vs01_1', Product='N-acetylmuramoyl-L-alanine amidase', 
# Protein_classification='unsorted;', Molecular_weight='4186.6396', Aromaticity=0.054054054054054, 
# Instability_index='22.98918918918919', Isoelectric_point=5.664426231384279, Helix_fraction=0.2702702702702703,
#  Turn_fraction=0.081081081081081, Sheet_fraction=0.4054054054054054, Reduced_coefficient=2980, Oxidized_coefficient=2980, Phage_source='CHVD')

def add_data():
    from phage_protein.models import phage_protein_IMG_VR,phage_protein_CHVD,phage_protein_IGVD,phage_protein_GOV2,phage_protein_STV
    baseurl = '/home/platform/phage_db/phage_data/data/csv_data/Download/Annotated_protein_meta_data_v2/'
    dataset = ['gov2_phage_annotated_protein_meta_data.tsv', 
                'igvd_phage_annotated_protein_meta_data.tsv', 
                'stv_phage_annotated_protein_meta_data.tsv', 
                'chvd_phage_annotated_protein_meta_data.tsv',
                'img_vr_phage_annotated_protein_meta_data.tsv']

    print(dataset[0])
    phage_protein = pd.read_csv(baseurl+dataset[0], sep='\t')
    for row in phage_protein.itertuples():
                phage_protein_GOV2.objects.create(
                Phage_Acession_ID=row.Phage_ID, Source=row.Protein_source, Start_location=row.Start, Stop_location=row.Stop, Strand=row.Strand, 
                Protein_id=row.Protein_ID, Protein_product=row.Product, Protein_function_classification=row.Protein_classification, molecular_weight=row.Molecular_weight, 
                aromaticity=row.Aromaticity, instability_index=row.Instability_index, isoelectric_point=row.Isoelectric_point, 
                Helix_secondary_structure_fraction=row.Helix_fraction, Turn_secondary_structure_fraction=row.Turn_fraction, Sheet_secondary_structure_fraction=row.Sheet_fraction, 
                Reduced_molar_extinction_coefficient=row.Reduced_coefficient, Oxidized_molar_extinction_coefficient=row.Oxidized_coefficient, dataset=row.Phage_source)

    print(dataset[1])
    phage_protein = pd.read_csv(baseurl+dataset[1], sep='\t')
    for row in phage_protein.itertuples():
                phage_protein_IGVD.objects.create(
                Phage_Acession_ID=row.Phage_ID, Source=row.Protein_source, Start_location=row.Start, Stop_location=row.Stop, Strand=row.Strand, 
                Protein_id=row.Protein_ID, Protein_product=row.Product, Protein_function_classification=row.Protein_classification, molecular_weight=row.Molecular_weight, 
                aromaticity=row.Aromaticity, instability_index=row.Instability_index, isoelectric_point=row.Isoelectric_point, 
                Helix_secondary_structure_fraction=row.Helix_fraction, Turn_secondary_structure_fraction=row.Turn_fraction, Sheet_secondary_structure_fraction=row.Sheet_fraction, 
                Reduced_molar_extinction_coefficient=row.Reduced_coefficient, Oxidized_molar_extinction_coefficient=row.Oxidized_coefficient, dataset=row.Phage_source)      

    print(dataset[2])
    phage_protein = pd.read_csv(baseurl+dataset[2], sep='\t')
    for row in phage_protein.itertuples():
                phage_protein_STV.objects.create(
                Phage_Acession_ID=row.Phage_ID, Source=row.Protein_source, Start_location=row.Start, Stop_location=row.Stop, Strand=row.Strand, 
                Protein_id=row.Protein_ID, Protein_product=row.Product, Protein_function_classification=row.Protein_classification, molecular_weight=row.Molecular_weight, 
                aromaticity=row.Aromaticity, instability_index=row.Instability_index, isoelectric_point=row.Isoelectric_point, 
                Helix_secondary_structure_fraction=row.Helix_fraction, Turn_secondary_structure_fraction=row.Turn_fraction, Sheet_secondary_structure_fraction=row.Sheet_fraction, 
                Reduced_molar_extinction_coefficient=row.Reduced_coefficient, Oxidized_molar_extinction_coefficient=row.Oxidized_coefficient, dataset=row.Phage_source)
    
    print(dataset[3])
    phage_protein = pd.read_csv(baseurl+dataset[3], sep='\t')
    for row in phage_protein.itertuples():
                phage_protein_CHVD.objects.create(
                Phage_Acession_ID=row.Phage_ID, Source=row.Protein_source, Start_location=row.Start, Stop_location=row.Stop, Strand=row.Strand, 
                Protein_id=row.Protein_ID, Protein_product=row.Product, Protein_function_classification=row.Protein_classification, molecular_weight=row.Molecular_weight, 
                aromaticity=row.Aromaticity, instability_index=row.Instability_index, isoelectric_point=row.Isoelectric_point, 
                Helix_secondary_structure_fraction=row.Helix_fraction, Turn_secondary_structure_fraction=row.Turn_fraction, Sheet_secondary_structure_fraction=row.Sheet_fraction, 
                Reduced_molar_extinction_coefficient=row.Reduced_coefficient, Oxidized_molar_extinction_coefficient=row.Oxidized_coefficient, dataset=row.Phage_source)
    
    print(dataset[4])
    phage_protein = pd.read_csv(baseurl+dataset[4], sep='\t')
    for row in phage_protein.itertuples():
                phage_protein_IMG_VR.objects.create(
                Phage_Acession_ID=row.Phage_ID, Source=row.Protein_source, Start_location=row.Start, Stop_location=row.Stop, Strand=row.Strand, 
                Protein_id=row.Protein_ID, Protein_product=row.Product, Protein_function_classification=row.Protein_classification, molecular_weight=row.Molecular_weight, 
                aromaticity=row.Aromaticity, instability_index=row.Instability_index, isoelectric_point=row.Isoelectric_point, 
                Helix_secondary_structure_fraction=row.Helix_fraction, Turn_secondary_structure_fraction=row.Turn_fraction, Sheet_secondary_structure_fraction=row.Sheet_fraction, 
                Reduced_molar_extinction_coefficient=row.Reduced_coefficient, Oxidized_molar_extinction_coefficient=row.Oxidized_coefficient, dataset=row.Phage_source)




if __name__ == "__main__":
    add_data()
