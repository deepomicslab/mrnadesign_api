from django.db import models
from phage.models import phage


# trna_id, trnatype, start, end, strand,length,permutation,seq,phage_accid


class phage_trna(models.Model):
    trna_id = models.CharField(max_length=200, blank=True, null=True)
    trnatype = models.CharField(max_length=200, blank=True, null=True)
    start = models.CharField(max_length=50, blank=True, null=True)
    end = models.CharField(max_length=50, blank=True, null=True)
    strand = models.CharField(max_length=20, blank=True, null=True)
    length = models.IntegerField(blank=True, null=True)
    permutation = models.TextField(blank=True, null=True)
    seq = models.TextField(blank=True, null=True)
    phage_accid = models.CharField(max_length=200, blank=True, null=True)
    phage = models.ForeignKey(phage, on_delete=models.DO_NOTHING)

    class Meta:
        db_table = 'phage_trna'
        verbose_name = 'phage_trna'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.trna_id
