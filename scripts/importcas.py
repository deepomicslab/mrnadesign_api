import django
import os
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

# ['Strain', 'Sequence', 'Sequence_basename', 'Duplicated_Spacers',
#        'CRISPR_Id', 'CRISPR_Start', 'CRISPR_End', 'CRISPR_Length',
#        'Potential_Orientation (AT%)', 'CRISPRDirection', 'Consensus_Repeat',
#        'Repeat_ID (CRISPRdb)', 'Nb_CRISPRs_with_same_Repeat (CRISPRdb)',
#        'Repeat_Length', 'Spacers_Nb', 'Mean_size_Spacers',
#        'Standard_Deviation_Spacers', 'Nb_Repeats_matching_Consensus',
#        'Ratio_Repeats_match/TotalRepeat', 'Conservation_Repeats (% identity)',
#        'EBcons_Repeats', 'Conservation_Spacers (% identity)', 'EBcons_Spacers',
#        'Repeat_Length_plus_mean_size_Spacers',
#        'Ratio_Repeat/mean_Spacers_Length',
#        'CRISPR_found_in_DB (if sequence IDs are similar)', 'Evidence_Level']


def add_data():
    from phage_protein.models import phage_crispr

    with open('/home/platform/phage_db/phage_api/workspace/rawd_data/csv/CRISPR_all_result.tsv', 'r') as f:
        lines = f.readlines()

    for line in lines:
        if 'AT%' in line:
            continue
        else:
            l = line.strip().split("\t")

            phage_crispr.objects.create(
                Strain=l[0], Phage_id=l[1], Sequence_basename=l[2], Duplicated_Spacers=l[3], CRISPR_Id=l[4], CRISPR_Start=l[5], CRISPR_End=l[6], CRISPR_Length=l[7], Potential_Orientation_AT=l[8], CRISPRDirection=l[9], Consensus_Repeat=l[10], Repeat_ID_CRISPRdb=l[11], Nb_CRISPRs_with_same_Repeat_CRISPRdb=l[12], Repeat_Length=l[13], Spacers_Nb=l[14], Mean_size_Spacers=l[15], Standard_Deviation_Spacers=l[16], Nb_Repeats_matching_Consensus=l[17], Ratio_Repeats_match_TotalRepeat=l[18], Conservation_Repeats_identity=l[19], EBcons_Repeats=l[20], Conservation_Spacers_identity=l[21], EBcons_Spacers=l[22], Repeat_Length_plus_mean_size_Spacers=l[23], Ratio_Repeat_mean_Spacers_Length=l[24], CRISPR_found_in_DB_if_sequence_IDs_are_similar=l[25], Evidence_Level=l[26])


if __name__ == "__main__":
    add_data()
