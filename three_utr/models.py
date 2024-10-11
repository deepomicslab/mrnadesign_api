from django.db import models

class three_utr(models.Model):
    gene_name = models.CharField(max_length=100, blank=True, null=True)
    ensembl_gene_id = models.CharField(max_length=100, blank=True, null=True)
    ensembl_transcript_id = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(max_length=300, blank=True, null=True)
    start_position = models.IntegerField(blank=True, null=True)
    end_position = models.IntegerField(blank=True, null=True)
    pattern = models.CharField(max_length=100, blank=True, null=True)
    cluster = models.IntegerField(blank=True, null=True)
    chromosome = models.CharField(max_length=100, blank=True, null=True)
    aliases = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        db_table = 'three_utr'
        verbose_name = 'three_utr'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.gene_name
