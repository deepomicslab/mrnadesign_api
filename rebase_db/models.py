from django.db import models
from django.contrib.postgres.fields import ArrayField

class rebase_data(models.Model):
    accession_number = models.CharField(max_length=200, blank=True, null=True)
    recognition_seq_w_cleavage_site = models.CharField(max_length=200, blank=True, null=True)
    recognition_site = models.CharField(max_length=200, blank=True, null=True)
    enzyme_name_list = ArrayField(
        models.CharField(max_length=200, blank=True, null=True),
    )
    enzyme_type = models.CharField(max_length=200, blank=True, null=True)
    suppliers = models.TextField(blank=True, null=True)
    prototype = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        db_table = 'rebase_data'
        verbose_name = 'rebase_data'
        verbose_name_plural = verbose_name

    def __str__(self):

        return self.accession_number
    
class rebase_enzyme_link(models.Model):
    enzyme_name = models.CharField(max_length=200, blank=True, null=True)
    enzyme_page = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        db_table = 'rebase_enzyme_link'
        verbose_name = 'rebase_enzyme_link'
        verbose_name_plural = verbose_name

    def __str__(self):

        return self.enzyme_name