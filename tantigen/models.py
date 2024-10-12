from django.db import models

class tantigen(models.Model):
    # shared fields
    agacc = models.CharField(max_length=20, blank=True, null=True)
    antigen_name = models.CharField(max_length=200, blank=True, null=True)
    # from Tantigendb_se.scv
    full_name = models.CharField(max_length=200, blank=True, null=True)
    synonym = models.TextField(blank=True, null=True)
    uniprot_id = models.CharField(max_length=20, blank=True, null=True)
    href1 = models.TextField(max_length=200, blank=True, null=True)
    ncbi_gene_id = models.CharField(max_length=20, blank=True, null=True)
    href2 = models.TextField(max_length=200, blank=True, null=True)
    gene_card_id = models.CharField(max_length=20, blank=True, null=True)
    href3 = models.TextField(max_length=200, blank=True, null=True)
    rna_or_protein_expression_profile = models.CharField(max_length=100, blank=True, null=True)
    href4 = models.TextField(max_length=200, blank=True, null=True)
    antigen_sequence = models.TextField(blank=True, null=True)  
    # from Tantigen_rna_seq.csv
    seq_5 = models.TextField(blank=True, null=True)
    cds = models.TextField(blank=True, null=True)
    seq_3 = models.TextField(blank=True, null=True)  

    class Meta:
        db_table = 'tantigen'
        verbose_name = 'tantigen'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.agacc
    
