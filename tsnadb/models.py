from django.db import models

class tsnadb_validated(models.Model):
    level = models.CharField(max_length=200, blank=True, null=True)
    patient_id = models.CharField(max_length=200, blank=True, null=True)
    tumor_type = models.CharField(max_length=200, blank=True, null=True)
    tumor_type_detaile = models.CharField(max_length=200, blank=True, null=True)
    mutation_type = models.CharField(max_length=200, blank=True, null=True)
    gene = models.CharField(max_length=200, blank=True, null=True)
    mutation = models.CharField(max_length=200, blank=True, null=True)
    position = models.CharField(max_length=200, blank=True, null=True)
    mutant_peptide = models.CharField(max_length=200, blank=True, null=True)
    hla = models.CharField(max_length=200, blank=True, null=True)
    pubmed_id = models.CharField(max_length=200, blank=True, null=True)
    reference_name = models.CharField(max_length=500, blank=True, null=True)
    journal = models.CharField(max_length=200, blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    doi = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        db_table = 'tsnadb_validated'
        verbose_name = 'tsnadb_validated'
        verbose_name_plural = verbose_name

    def __str__(self):

        return self.id

class tsnadb_neoantigen(models.Model):
    type = models.CharField(max_length=200, blank=True, null=True)
    tissue = models.CharField(max_length=200, blank=True, null=True)
    mutation = models.CharField(max_length=200, blank=True, null=True)
    hla = models.CharField(max_length=200, blank=True, null=True)
    peptide = models.CharField(max_length=200, blank=True, null=True)
    deep_bind = models.FloatField(blank=True, null=True)
    deep_imm = models.FloatField(blank=True, null=True)
    nhcf_rank_percent = models.FloatField(blank=True, null=True)
    net4_aff_nm = models.FloatField(blank=True, null=True)
    net4_aff_percent = models.FloatField(blank=True, null=True)
    tpm = models.FloatField(blank=True, null=True)
    frequency_in_the_tissue = models.CharField(max_length=200, blank=True, null=True)
    frequency_in_all_samples = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        db_table = 'tsnadb_neoantigen'
        verbose_name = 'tsnadb_neoantigen'
        verbose_name_plural = verbose_name

    def __str__(self):

        return self.id
