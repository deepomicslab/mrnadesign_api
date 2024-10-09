import django
import os
import pandas as pd
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Phage_api.settings")

django.setup()

# Strain = models.CharField(max_length=200, blank=True, null=True)
# Phage_id = models.CharField(max_length=200, blank=True, null=True)
# Sequence_basename = models.CharField(max_length=200, blank=True, null=True)
# Duplicated_Spacers = models.CharField(
#     max_length=200, blank=True, null=True)
# CRISPR_Id = models.CharField(max_length=200, blank=True, null=True)
# CRISPR_Start = models.CharField(max_length=200, blank=True, null=True)
# CRISPR_End = models.CharField(max_length=200, blank=True, null=True)
# CRISPR_Length = models.CharField(max_length=200, blank=True, null=True)
# Potential_Orientation_AT = models.CharField(
#     max_length=200, blank=True, null=True)
# CRISPRDirection = models.CharField(max_length=200, blank=True, null=True)
# Consensus_Repeat = models.CharField(max_length=200, blank=True, null=True)
# Repeat_ID_CRISPRdb = models.CharField(
#     max_length=200, blank=True, null=True)
# Nb_CRISPRs_with_same_Repeat_CRISPRdb = models.CharField(
#     max_length=200, blank=True, null=True)
# Repeat_Length = models.CharField(max_length=200, blank=True, null=True)
# Spacers_Nb = models.CharField(max_length=200, blank=True, null=True)
# Mean_size_Spacers = models.CharField(max_length=200, blank=True, null=True)
# Standard_Deviation_Spacers = models.CharField(
#     max_length=200, blank=True, null=True)
# Nb_Repeats_matching_Consensus = models.CharField(
#     max_length=200, blank=True, null=True)
# Ratio_Repeats_match_TotalRepeat = models.CharField(
#     max_length=200, blank=True, null=True)
# Conservation_Repeats_identity = models.CharField(
#     max_length=200, blank=True, null=True)
# EBcons_Repeats = models.CharField(max_length=200, blank=True, null=True)
# Conservation_Spacers_identity = models.CharField(
#     max_length=200, blank=True, null=True)
# EBcons_Spacers = models.CharField(max_length=200, blank=True, null=True)
# Repeat_Length_plus_mean_size_Spacers = models.CharField(
#     max_length=200, blank=True, null=True)
# Ratio_Repeat_mean_Spacers_Length = models.CharField(
#     max_length=200, blank=True, null=True)
# CRISPR_found_in_DB_if_sequence_IDs_are_similar = models.CharField(
#     max_length=200, blank=True, null=True)
# Evidence_Level = models.CharField(max_length=200, blank=True, null=True)


def add_data():
    from phage_protein.models import phage_crispr


#Strain	Sequence	Sequence_basename	Duplicated_Spacers	CRISPR_Id	CRISPR_Start	CRISPR_End	CRISPR_Length	
# Potential_Orientation (AT%)	CRISPRDirection	Consensus_Repeat	Repeat_ID (CRISPRdb)	Nb_CRISPRs_with_same_Repeat (CRISPRdb)	
# Repeat_Length	Spacers_Nb	Mean_size_Spacers	Standard_Deviation_Spacers	Nb_Repeats_matching_Consensus	
# Ratio_Repeats_match/TotalRepeat	Conservation_Repeats (% identity)	EBcons_Repeats	Conservation_Spacers (% identity)	
# EBcons_Spacers	Repeat_Length_plus_mean_size_Spacers	Ratio_Repeat/mean_Spacers_Length	CRISPR_found_in_DB (if sequence IDs are similar)	
# Evidence_Level	
    cas=pd.read_csv('/home/platform/phage_db/phage_api/workspace/data_revision/CRISPRCas.tsv',sep='\t')

    for index,row in cas.iterrows():
        phage_crispr.objects.create(Strain=row[0],Phage_id=row[1],Sequence_basename=row[2],Duplicated_Spacers=row[3],CRISPR_Id=row[4],
                                    CRISPR_Start=row[5],CRISPR_End=row[6],CRISPR_Length=row[7],Potential_Orientation_AT=row[8],
                                    CRISPRDirection=row[9],Consensus_Repeat=row[10],Repeat_ID_CRISPRdb=row[11],Nb_CRISPRs_with_same_Repeat_CRISPRdb=row[12],
                                    Repeat_Length=row[13],Spacers_Nb=row[14],Mean_size_Spacers=row[15],Standard_Deviation_Spacers=row[16],
                                    Nb_Repeats_matching_Consensus=row[17],Ratio_Repeats_match_TotalRepeat=row[18],Conservation_Repeats_identity=row[19],
                                    EBcons_Repeats=row[20],Conservation_Spacers_identity=row[21],EBcons_Spacers=row[22],Repeat_Length_plus_mean_size_Spacers=row[23],
                                    Ratio_Repeat_mean_Spacers_Length=row[24],CRISPR_found_in_DB_if_sequence_IDs_are_similar=row[25],Evidence_Level=row[26])
            


if __name__ == "__main__":
    add_data()