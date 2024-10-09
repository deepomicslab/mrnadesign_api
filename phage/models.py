from django.db import models
from datasets.models import datasets


class phage(models.Model):
    Acession_ID = models.CharField(max_length=200, blank=True, null=True)
    length = models.IntegerField(blank=True, null=True)
    gc_content = models.CharField(max_length=200, blank=True, null=True)
    host = models.TextField(blank=True, null=True)
    completeness = models.CharField(max_length=200, blank=True, null=True)
    taxonomy = models.CharField(max_length=200, blank=True, null=True)
    cluster = models.CharField(max_length=200, blank=True, null=True)
    subcluster = models.CharField(max_length=200, blank=True, null=True)
    Data_Sets = models.ForeignKey(datasets, on_delete=models.DO_NOTHING)
    reference = models.TextField(blank=True, null=True)
    display_id = models.IntegerField(default=1000)
    is_rep=models.BooleanField(default=False)
    is_redundant=models.BooleanField(default=False)

    class Meta:
        db_table = 'phages'
        verbose_name = 'phages'
        verbose_name_plural = verbose_name

    def __str__(self):

        return self.Acession_ID
