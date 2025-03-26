from django.db import models

class BaseTissue(models.Model):
    # naming: 
    # i.lower().replace(' - ', '_').replace(' ', '_').replace('(', '').replace(')', '').replace('-', '_')
    genomic = models.FloatField(null=True, blank=True)
    adipose_subcutaneous = models.FloatField()
    adipose_visceral_omentum = models.FloatField()
    adrenal_gland = models.FloatField()
    artery_aorta = models.FloatField()
    artery_coronary = models.FloatField()
    artery_tibial = models.FloatField()
    bladder = models.FloatField()
    brain_amygdala = models.FloatField()
    brain_anterior_cingulate_cortex_ba24 = models.FloatField()
    brain_caudate_basal_ganglia = models.FloatField()
    brain_cerebellar_hemisphere = models.FloatField()
    brain_cerebellum = models.FloatField()
    brain_cortex = models.FloatField()
    brain_frontal_cortex_ba9 = models.FloatField()
    brain_hippocampus = models.FloatField()
    brain_hypothalamus = models.FloatField()
    brain_nucleus_accumbens_basal_ganglia = models.FloatField()
    brain_putamen_basal_ganglia = models.FloatField()
    brain_spinal_cord_cervical_c_1 = models.FloatField()
    brain_substantia_nigra = models.FloatField()
    breast_mammary_tissue = models.FloatField()
    cells_cultured_fibroblasts = models.FloatField()
    cells_ebv_transformed_lymphocytes = models.FloatField()
    cervix_ectocervix = models.FloatField()
    cervix_endocervix = models.FloatField()
    colon_sigmoid = models.FloatField()
    colon_transverse = models.FloatField()
    esophagus_gastroesophageal_junction = models.FloatField()
    esophagus_mucosa = models.FloatField()
    esophagus_muscularis = models.FloatField()
    fallopian_tube = models.FloatField()
    heart_atrial_appendage = models.FloatField()
    heart_left_ventricle = models.FloatField()
    kidney_cortex = models.FloatField()
    kidney_medulla = models.FloatField()
    liver = models.FloatField()
    lung = models.FloatField()
    minor_salivary_gland = models.FloatField()
    muscle_skeletal = models.FloatField()
    nerve_tibial = models.FloatField()
    ovary = models.FloatField()
    pancreas = models.FloatField()
    pituitary = models.FloatField()
    prostate = models.FloatField()
    skin_not_sun_exposed_suprapubic = models.FloatField()
    skin_sun_exposed_lower_leg = models.FloatField()
    small_intestine_terminal_ileum = models.FloatField()
    spleen = models.FloatField()
    stomach = models.FloatField()
    testis = models.FloatField()
    thyroid = models.FloatField()
    uterus = models.FloatField()
    vagina = models.FloatField()
    whole_blood = models.FloatField()

    class Meta:
        db_table = 'BaseTissue'
        verbose_name = 'BaseTissue'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.id
    
class CodonPair(BaseTissue):
    Dinucleotide = models.CharField(max_length=200) # codon pair
    calculation_type = models.CharField(max_length=100) # fraction, counts, frequency
    
    class Meta:
        db_table = 'CodonPair'
        verbose_name = 'CodonPair'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.Dinucleotide+'_'+self.calculation_type