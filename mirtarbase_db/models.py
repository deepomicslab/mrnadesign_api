from django.db import models

class mirtarbase_db(models.Model):
    mirtarbase_id = models.CharField(max_length=200) # not unique
    mirna = models.CharField(max_length=200, blank=True, null=True)
    species_mirna = models.CharField(max_length=200, blank=True, null=True)
    target_gene = models.CharField(max_length=200, blank=True, null=True)
    target_gene_entrez_gene_id = models.CharField(max_length=200, blank=True, null=True)
    species_target_gene = models.CharField(max_length=200, blank=True, null=True)
    target_site = models.TextField(blank=True, null=True)
    experiments = models.TextField(blank=True, null=True)
    support_type = models.CharField(max_length=200, blank=True, null=True)
    references_pmid = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        db_table = 'mirtarbase_db'
        verbose_name = 'mirtarbase_db'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.id