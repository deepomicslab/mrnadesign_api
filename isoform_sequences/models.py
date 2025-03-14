from django.db import models
from django.utils import timezone


class isoform(models.Model):
    isoform_id = models.CharField(max_length=200, blank=True, null=True, unique=True)
    gene_id = models.CharField(max_length=200, blank=True, null=True)
    gene_name = models.CharField(max_length=200, blank=True, null=True)
    chromosome = models.CharField(max_length=200, blank=True, null=True)
    start_pos = models.IntegerField()
    end_pos = models.IntegerField()
    junction_position = models.TextField(blank=True, null=True)
    strand = models.CharField(max_length=200, blank=True, null=True)
    isoform_type = models.CharField(max_length=200, blank=True, null=True)
    exon_count = models.IntegerField()
    create_time = models.DateTimeField(auto_created=True, default=timezone.now)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'isoform'
        verbose_name = 'isoform'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.isoform_id


class gene(models.Model):
    gene_id = models.CharField(max_length=200, blank=True, null=True, unique=True)
    gene_name = models.CharField(max_length=200, blank=True, null=True)
    chromosome = models.CharField(max_length=200, blank=True, null=True)
    start_pos = models.IntegerField()
    end_pos = models.IntegerField()
    strand = models.CharField(max_length=200, blank=True, null=True)
    gene_type = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        db_table = 'gene'
        verbose_name = 'gene'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.gene_name
