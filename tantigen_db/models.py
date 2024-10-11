from django.db import models

class tantigen_db(models.Model):
    agacc = models.CharField(max_length=20, blank=True, null=True)
    antigen_name = models.CharField(max_length=200, blank=True, null=True)
    full_name = models.CharField(max_length=200, blank=True, null=True)
    synonym = models.TextField(blank=True, null=True)
    uniprot_id = models.CharField(max_length=20, blank=True, null=True)
    href1 = models.TextField(max_length=200, blank=True, null=True)
    ncbi_gene_id = models.CharField(max_length=20, blank=True, null=True)
    href2 = models.TextField(max_length=200, blank=True, null=True)
    gene_card_id = models.CharField(max_length=20, blank=True, null=True)
    href3 = models.TextField(max_length=200, blank=True, null=True)
    isoforms = models.CharField(max_length=10, blank=True, null=True)
    rna_or_protein_expression_profile = models.CharField(max_length=100, blank=True, null=True)
    href4 = models.TextField(max_length=200, blank=True, null=True)
    antigen_sequence = models.TextField(blank=True, null=True)    

    class Meta:
        db_table = 'tantigen_db'
        verbose_name = 'tantigen_db'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.agacc
    
