from django.db import models

# ['Genbank', 'RefSeq', 'DDBJ', 'EMBL', 'tpg', 'PhagesDB', 'GPD', 'GVD', 'MGV', 'TemPhD']

class AbstractProtein(models.Model):
    Phage_Acession_ID = models.CharField(max_length=200, blank=True, null=True)
    Source = models.CharField(max_length=30, blank=True, null=True)

    Start_location = models.IntegerField(blank=True, null=True)
    Stop_location = models.IntegerField(blank=True, null=True)
    Strand = models.CharField(max_length=10, blank=True, null=True)

    Protein_id = models.CharField(max_length=220, blank=True, null=True)

    Protein_product = models.TextField(blank=True, null=True)
    Protein_function_classification = models.TextField(blank=True, null=True)
    Function_prediction_source=models.CharField(max_length=80, blank=True, null=True)
    molecular_weight = models.CharField(max_length=100, blank=True, null=True)
    aromaticity = models.CharField(max_length=100, blank=True, null=True)
    instability_index = models.CharField(max_length=100, blank=True, null=True)
    isoelectric_point = models.CharField(max_length=100, blank=True, null=True)
    Helix_secondary_structure_fraction = models.CharField(max_length=100, blank=True, null=True)
    Turn_secondary_structure_fraction = models.CharField(max_length=100, blank=True, null=True)
    Sheet_secondary_structure_fraction = models.CharField(max_length=100, blank=True, null=True)
    Reduced_molar_extinction_coefficient = models.CharField(max_length=100, blank=True, null=True)
    Oxidized_molar_extinction_coefficient = models.CharField(max_length=100, blank=True, null=True)

    dataset = models.CharField(max_length=10, blank=True, null=True)
    prosequence = models.TextField(blank=True, null=True)

    class Meta:
        abstract = True
    def __str__(self):
        return self.Phage_Acession_ID

class phage_protein_NCBI(AbstractProtein):
    class Meta:
        db_table = 'phage_protein_NCBI'
        verbose_name = 'phage_protein_NCBI'
        verbose_name_plural = verbose_name
    def __str__(self):
        return self.Phage_Acession_ID

class phage_protein_PhagesDB(AbstractProtein):
    class Meta:
        db_table = 'phage_protein_PhagesDB'
        verbose_name = 'phage_protein_PhagesDB'
        verbose_name_plural = verbose_name
    def __str__(self):
        return self.Phage_Acession_ID

class phage_protein_GPD(AbstractProtein):
    class Meta:
        db_table = 'phage_protein_GPD'
        verbose_name = 'phage_protein_GPD'
        verbose_name_plural = verbose_name
    def __str__(self):
        return self.Phage_Acession_ID

class phage_protein_GVD(AbstractProtein):
    class Meta:
        db_table = 'phage_protein_GVD'
        verbose_name = 'phage_protein_GVD'
        verbose_name_plural = verbose_name
    def __str__(self):
        return self.Phage_Acession_ID

class phage_protein_MGV(AbstractProtein):
    class Meta:
        db_table = 'phage_protein_MGV'
        verbose_name = 'phage_protein_MGV'
        verbose_name_plural = verbose_name
    def __str__(self):
        return self.Phage_Acession_ID

class phage_protein_TemPhD(AbstractProtein):
    class Meta:
        db_table = 'phage_protein_TemPhD'
        verbose_name = 'phage_protein_TemPhD'
        verbose_name_plural = verbose_name
    def __str__(self):
        return self.Phage_Acession_ID

class phage_protein_IMG_VR(AbstractProtein):
    class Meta:
        db_table = 'phage_protein_IMG_VR'
        verbose_name = 'phage_protein_IMG_VR'
        verbose_name_plural = verbose_name
    def __str__(self):
        return self.Phage_Acession_ID

class phage_protein_CHVD(AbstractProtein):
    class Meta:
        db_table = 'phage_protein_CHVD'
        verbose_name = 'phage_protein_CHVD'
        verbose_name_plural = verbose_name
    def __str__(self):
        return self.Phage_Acession_ID

class phage_protein_IGVD(AbstractProtein):
    class Meta:
        db_table = 'phage_protein_IGVD'
        verbose_name = 'phage_protein_IGVD'
        verbose_name_plural = verbose_name
    def __str__(self):
        return self.Phage_Acession_ID

class phage_protein_GOV2(AbstractProtein):
    class Meta:
        db_table = 'phage_protein_GOV2'
        verbose_name = 'phage_protein_GOV2'
        verbose_name_plural = verbose_name
    def __str__(self):
        return self.Phage_Acession_ID

class phage_protein_STV(AbstractProtein):
    class Meta:
        db_table = 'phage_protein_STV'
        verbose_name = 'phage_protein_STV'
        verbose_name_plural = verbose_name
    def __str__(self):
        return self.Phage_Acession_ID

class phage_protein_anticrispr(models.Model):
    Protein_id = models.CharField(max_length=200, blank=True, null=True)
    Source = models.CharField(max_length=200, blank=True, null=True)
    Phage_Acession_ID = models.CharField(max_length=200, blank=True, null=True)
    dataset = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        db_table = 'phage_protein_anticrispr'
        verbose_name = 'phage_protein_anticrispr'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.Protein_id












class AbstractTmhmmProtein(models.Model):
    Protein_id = models.CharField(max_length=200, blank=True, null=True)
    Phage_Acession_ID = models.CharField(max_length=200, blank=True, null=True)
    Length = models.CharField(max_length=200, blank=True, null=True)
    predictedTMHsNumber = models.CharField(
        max_length=200, blank=True, null=True)
    ExpnumberofAAsinTMHs = models.CharField(
        max_length=200, blank=True, null=True)
    Expnumberfirst60AAs = models.CharField(
        max_length=200, blank=True, null=True)
    TotalprobofNin = models.CharField(max_length=200, blank=True, null=True)
    POSSIBLENterm = models.CharField(max_length=200, blank=True, null=True)
    insidesource = models.CharField(max_length=200, blank=True, null=True)
    insidestart = models.CharField(max_length=200, blank=True, null=True)
    insideend = models.CharField(max_length=200, blank=True, null=True)
    TMhelixsource = models.CharField(max_length=200, blank=True, null=True)
    TMhelixstart = models.CharField(max_length=200, blank=True, null=True)
    TMhelixend = models.CharField(max_length=200, blank=True, null=True)
    outsidesource = models.CharField(max_length=200, blank=True, null=True)
    outsidestart = models.CharField(max_length=200, blank=True, null=True)
    outsideend = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        abstract = True
    def __str__(self):
        return self.Phage_Acession_ID


# phageid    Length  predictedTMHsNumber ExpnumberofAAsinTMHs    Expnumberfirst60AAs TotalprobofNin  POSSIBLENterm   insidesource    insidestart insideend   TMhelixsource   TMhelixstart    TMhelixend  outsidesource   outsidestart    outsideend
class phage_protein_tmhmm_NCBI(AbstractTmhmmProtein):
    class Meta:
        db_table = 'phage_protein_tmhmm_NCBI'
        verbose_name = 'phage_protein_tmhmm_NCBI'
        verbose_name_plural = verbose_name
    def __str__(self):
        return self.Phage_Acession_ID

class phage_protein_tmhmm_PhagesDB(AbstractTmhmmProtein):
    class  Meta:
        db_table = 'phage_protein_tmhmm_PhagesDB'
        verbose_name = 'phage_protein_tmhmm_PhagesDB'
        verbose_name_plural = verbose_name
    def __str__(self):
        return self.Phage_Acession_ID
    

class phage_protein_tmhmm_GPD(AbstractTmhmmProtein):
    class Meta:
        db_table = 'phage_protein_tmhmm_GPD'
        verbose_name = 'phage_protein_tmhmm_GPD'
        verbose_name_plural = verbose_name
    def __str__(self):
        return self.Phage_Acession_ID

class phage_protein_tmhmm_GVD(AbstractTmhmmProtein):
    class Meta:
        db_table = 'phage_protein_tmhmm_GVD'
        verbose_name = 'phage_protein_tmhmm_GVD'
        verbose_name_plural = verbose_name
    def __str__(self):
        return self.Phage_Acession_ID


class phage_protein_tmhmm_MGV(AbstractTmhmmProtein):
    class Meta:
        db_table = 'phage_protein_tmhmm_MGV'
        verbose_name = 'phage_protein_tmhmm_MGV'
        verbose_name_plural = verbose_name
    def __str__(self):
        return self.Phage_Acession_ID

class phage_protein_tmhmm_TemPhD(AbstractTmhmmProtein):
    class Meta:
        db_table = 'phage_protein_tmhmm_TemPhD'
        verbose_name = 'phage_protein_tmhmm_TemPhD'
        verbose_name_plural = verbose_name
    def __str__(self):
        return self.Phage_Acession_ID

class phage_protein_tmhmm_STV(AbstractTmhmmProtein):
    class Meta:
        db_table = 'phage_protein_tmhmm_STV'
        verbose_name = 'phage_protein_tmhmm_STV'
        verbose_name_plural = verbose_name
    def __str__(self):
        return self.Phage_Acession_ID
class phage_protein_tmhmm_IGVD(AbstractTmhmmProtein):
    class Meta:
        db_table = 'phage_protein_tmhmm_IGVD'
        verbose_name = 'phage_protein_tmhmm_IGVD'
        verbose_name_plural = verbose_name
    def __str__(self):
        return self.Phage_Acession_ID
class phage_protein_tmhmm_GOV2(AbstractTmhmmProtein):
    class Meta:
        db_table = 'phage_protein_tmhmm_GOV2'
        verbose_name = 'phage_protein_tmhmm_GOV2'
        verbose_name_plural = verbose_name
    def __str__(self):
        return self.Phage_Acession_ID
class phage_protein_tmhmm_CHVD(AbstractTmhmmProtein):
    class Meta:
        db_table = 'phage_protein_tmhmm_CHVD'
        verbose_name = 'phage_protein_tmhmm_CHVD'
        verbose_name_plural = verbose_name
    def __str__(self):
        return self.Phage_Acession_ID
class phage_protein_tmhmm_IMG_VR(AbstractTmhmmProtein):
    class Meta:
        db_table = 'phage_protein_tmhmm_IMG_VR'
        verbose_name = 'phage_protein_tmhmm_IMG_VR'
        verbose_name_plural = verbose_name
    def __str__(self):
        return self.Phage_Acession_ID


class phage_crispr(models.Model):
    Strain = models.CharField(max_length=200, blank=True, null=True)
    Phage_id = models.CharField(max_length=200, blank=True, null=True)
    Sequence_basename = models.CharField(max_length=200, blank=True, null=True)
    Duplicated_Spacers = models.CharField(
        max_length=200, blank=True, null=True)
    CRISPR_Id = models.CharField(max_length=200, blank=True, null=True)
    CRISPR_Start = models.CharField(max_length=200, blank=True, null=True)
    CRISPR_End = models.CharField(max_length=200, blank=True, null=True)
    CRISPR_Length = models.CharField(max_length=200, blank=True, null=True)
    Potential_Orientation_AT = models.CharField(
        max_length=200, blank=True, null=True)
    CRISPRDirection = models.CharField(max_length=200, blank=True, null=True)
    Consensus_Repeat = models.CharField(max_length=200, blank=True, null=True)
    Repeat_ID_CRISPRdb = models.CharField(
        max_length=200, blank=True, null=True)
    Nb_CRISPRs_with_same_Repeat_CRISPRdb = models.CharField(
        max_length=200, blank=True, null=True)
    Repeat_Length = models.CharField(max_length=200, blank=True, null=True)
    Spacers_Nb = models.CharField(max_length=200, blank=True, null=True)
    Mean_size_Spacers = models.CharField(max_length=200, blank=True, null=True)
    Standard_Deviation_Spacers = models.CharField(
        max_length=200, blank=True, null=True)
    Nb_Repeats_matching_Consensus = models.CharField(
        max_length=200, blank=True, null=True)
    Ratio_Repeats_match_TotalRepeat = models.CharField(
        max_length=200, blank=True, null=True)
    Conservation_Repeats_identity = models.CharField(
        max_length=200, blank=True, null=True)
    EBcons_Repeats = models.CharField(max_length=200, blank=True, null=True)
    Conservation_Spacers_identity = models.CharField(
        max_length=200, blank=True, null=True)
    EBcons_Spacers = models.CharField(max_length=200, blank=True, null=True)
    Repeat_Length_plus_mean_size_Spacers = models.CharField(
        max_length=200, blank=True, null=True)
    Ratio_Repeat_mean_Spacers_Length = models.CharField(
        max_length=200, blank=True, null=True)
    CRISPR_found_in_DB_if_sequence_IDs_are_similar = models.CharField(
        max_length=200, blank=True, null=True)
    Evidence_Level = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        db_table = 'phage_crispr'
        verbose_name = 'phage_crispr'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.CRISPR_Id


class phage_terminators(models.Model):
    # Phage_ID	Terminator	Start	Stop	Sense	Loc	Confidence
    Phage_id = models.CharField(max_length=500, blank=True, null=True)
    Terminator_Id = models.CharField(max_length=200, blank=True, null=True)
    Start = models.CharField(max_length=200, blank=True, null=True)
    Stop = models.CharField(max_length=200, blank=True, null=True)
    Sense = models.CharField(max_length=200, blank=True, null=True)
    Loc = models.CharField(max_length=200, blank=True, null=True)
    Confidence = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        db_table = 'phage_terminators'
        verbose_name = 'phage_terminators'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.Terminator_Id



class phage_antimicrobial_resistance_gene(models.Model):
    Protein_id = models.CharField(max_length=200, blank=True, null=True)
    Aligned_Protein_in_CARD  = models.CharField(max_length=200, blank=True, null=True)
    Phage_Acession_ID = models.CharField(max_length=200, blank=True, null=True)
    dataset = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        db_table = 'phage_antimicrobial_resistance_gene'
        verbose_name = 'phage_antimicrobial_resistance_gene'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.Protein_id
    

class phage_virulent_factor(models.Model):
    Protein_id = models.CharField(max_length=200, blank=True, null=True)
    Aligned_Protein_in_VFDB   = models.CharField(max_length=200, blank=True, null=True)
    Phage_Acession_ID = models.CharField(max_length=200, blank=True, null=True)
    dataset = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        db_table = 'phage_virulent_factor'
        verbose_name = 'phage_virulent_factor'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.Protein_id