from django.db import models
from phage.models import phage


class phage_hosts(models.Model):
    accesion_id = models.CharField(max_length=200, blank=True, null=True)
    host = models.TextField(blank=True, null=True)
    host_source = models.CharField(max_length=100, blank=True, null=True)
    Species = models.CharField(max_length=200, blank=True, null=True)
    Genus = models.CharField(max_length=200, blank=True, null=True)
    Family = models.CharField(max_length=200, blank=True, null=True)
    Order = models.CharField(max_length=200, blank=True, null=True)
    Class = models.CharField(max_length=200, blank=True, null=True)
    Phylum = models.CharField(max_length=200, blank=True, null=True)
    phage = models.ForeignKey(phage, on_delete=models.DO_NOTHING)

    class Meta:
        db_table = 'phage_hosts'
        verbose_name = 'phage_hosts'
        verbose_name_plural = verbose_name

    def __str__(self):

        return self.host


class phage_hostnode(models.Model):
    node = models.CharField(max_length=200, blank=True, null=True)
    parent = models.CharField(max_length=200, blank=True, null=True)
    rank = models.CharField(max_length=200, blank=True, null=True)
    phagecount = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'phage_hostnode'
        verbose_name = 'phage_hostnode'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.node
