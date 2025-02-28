from django.db import models

class utrdb(models.Model):
    utr_type = models.CharField(max_length=200, blank=True, null=True)
    transcript_id = models.CharField(max_length=200, blank=True, null=True)
    gene_id = models.CharField(max_length=200, blank=True, null=True)
    chr_start_end_strand = models.CharField(blank=True, null=True) # chr:start-end:strand
    sequence = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'utrdb'
        verbose_name = 'utrdb'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.id