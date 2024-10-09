import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Phage_api.settings")

django.setup()
# ['Genbank', 'RefSeq', 'DDBJ', 'EMBL', 'tpg', 'PhagesDB', 'GPD', 'GVD', 'MGV', 'TemPhD']


def add_data():
    from phage_protein.models import phage_protein_NCBI, phage_protein_PhagesDB, phage_protein_GPD, phage_protein_MGV, phage_protein_TemPhD, phage_protein_GVD
    baseurl = '/home/platform/phage_db/phage_api/workspace/csv_data/protein/'
    # dataset = ['ncbi', '6', '7', '8', '9', '10']
    # ncbi,6,8 10
    dataset = ['10']
    for i in dataset:
        print(i)
        with open(baseurl+i+'.csv', 'r') as f:
            lines = f.readlines()

        for line in lines:
            l = line.strip().split("\t")
            if i == 'ncbi':
                phage_protein_NCBI.objects.create(
                    Phage_Acession_ID=l[0], Source=l[1], Start_location=l[2], Stop_location=l[3], Strand=l[4], Protein_id=l[5], Protein_product=l[6], Protein_function_classification=l[7], molecular_weight=l[8], aromaticity=l[9], instability_index=l[10], isoelectric_point=l[11], Helix_secondary_structure_fraction=l[12], Turn_secondary_structure_fraction=l[13], Sheet_secondary_structure_fraction=l[14], Reduced_molar_extinction_coefficient=l[15], Oxidized_molar_extinction_coefficient=l[16], dataset=l[17])
            elif i == '6':
                phage_protein_PhagesDB.objects.create(
                    Phage_Acession_ID=l[0], Source=l[1], Start_location=l[2], Stop_location=l[3], Strand=l[4], Protein_id=l[5], Protein_product=l[6], Protein_function_classification=l[7], molecular_weight=l[8], aromaticity=l[9], instability_index=l[10], isoelectric_point=l[11], Helix_secondary_structure_fraction=l[12], Turn_secondary_structure_fraction=l[13], Sheet_secondary_structure_fraction=l[14], Reduced_molar_extinction_coefficient=l[15], Oxidized_molar_extinction_coefficient=l[16], dataset=l[17])
            elif i == '7':
                phage_protein_GPD.objects.create(
                    Phage_Acession_ID=l[0], Source=l[1], Start_location=l[2], Stop_location=l[3], Strand=l[4], Protein_id=l[5], Protein_product=l[6], Protein_function_classification=l[7], molecular_weight=l[8], aromaticity=l[9], instability_index=l[10], isoelectric_point=l[11], Helix_secondary_structure_fraction=l[12], Turn_secondary_structure_fraction=l[13], Sheet_secondary_structure_fraction=l[14], Reduced_molar_extinction_coefficient=l[15], Oxidized_molar_extinction_coefficient=l[16], dataset=l[17])
            elif i == '8':
                phage_protein_GVD.objects.create(
                    Phage_Acession_ID=l[0], Source=l[1], Start_location=l[2], Stop_location=l[3], Strand=l[4], Protein_id=l[5], Protein_product=l[6], Protein_function_classification=l[7], molecular_weight=l[8], aromaticity=l[9], instability_index=l[10], isoelectric_point=l[11], Helix_secondary_structure_fraction=l[12], Turn_secondary_structure_fraction=l[13], Sheet_secondary_structure_fraction=l[14], Reduced_molar_extinction_coefficient=l[15], Oxidized_molar_extinction_coefficient=l[16], dataset=l[17])
            elif i == '9':
                phage_protein_MGV.objects.create(
                    Phage_Acession_ID=l[0], Source=l[1], Start_location=l[2], Stop_location=l[3], Strand=l[4], Protein_id=l[5], Protein_product=l[6], Protein_function_classification=l[7], molecular_weight=l[8], aromaticity=l[9], instability_index=l[10], isoelectric_point=l[11], Helix_secondary_structure_fraction=l[12], Turn_secondary_structure_fraction=l[13], Sheet_secondary_structure_fraction=l[14], Reduced_molar_extinction_coefficient=l[15], Oxidized_molar_extinction_coefficient=l[16], dataset=l[17])
            elif i == '10':
                phage_protein_TemPhD.objects.create(
                    Phage_Acession_ID=l[0], Source=l[1], Start_location=l[2], Stop_location=l[3], Strand=l[4], Protein_id=l[5], Protein_product=l[6], Protein_function_classification=l[7], molecular_weight=l[8], aromaticity=l[9], instability_index=l[10], isoelectric_point=l[11], Helix_secondary_structure_fraction=l[12], Turn_secondary_structure_fraction=l[13], Sheet_secondary_structure_fraction=l[14], Reduced_molar_extinction_coefficient=l[15], Oxidized_molar_extinction_coefficient=l[16], dataset=l[17])


if __name__ == "__main__":
    add_data()
