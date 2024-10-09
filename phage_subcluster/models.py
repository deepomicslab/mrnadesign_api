from django.db import models
from phage_clusters.models import phage_clusters
# Create your models here.

# cluster, representative sequence, member, average_length, average_gc,


class phage_subcluster(models.Model):
    subcluster = models.CharField(max_length=200, blank=True, null=True)
    repsequence = models.CharField(max_length=200, blank=True, null=True)
    member = models.IntegerField(blank=True, null=True)
    average_length = models.CharField(max_length=200, blank=True, null=True)
    average_gc = models.CharField(max_length=200, blank=True, null=True)
    host = models.TextField(blank=True, null=True)
    average_genes = models.CharField(max_length=200, blank=True, null=True)
    average_trna = models.CharField(max_length=200, blank=True, null=True)
    cluster = models.ForeignKey(phage_clusters, on_delete=models.DO_NOTHING)
    lifestyle = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        db_table = 'phage_subcluster'
        verbose_name = 'phage_subcluster'
        verbose_name_plural = verbose_name

    def __str__(self):

        return self.subcluster
