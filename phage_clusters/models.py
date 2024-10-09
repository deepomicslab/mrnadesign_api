from django.db import models


class phage_clusters(models.Model):
    cluster = models.CharField(max_length=200, blank=True, null=True)
    subclusters = models.IntegerField(blank=True, null=True)
    member = models.IntegerField(blank=True, null=True)
    average_length = models.CharField(max_length=200, blank=True, null=True)
    average_gc = models.CharField(max_length=200, blank=True, null=True)
    average_genes = models.CharField(max_length=200, blank=True, null=True)
    lifestyle = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        db_table = 'phage_clusters'
        verbose_name = 'phage_clusters'
        verbose_name_plural = verbose_name

    def __str__(self):

        return self.cluster
