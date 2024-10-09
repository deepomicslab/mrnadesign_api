from django.db import models
from phage.models import phage


class phage_lifestyle(models.Model):
    accesion_id = models.CharField(max_length=200, blank=True, null=True)
    lifestyle = models.CharField(max_length=50, blank=True, null=True)
    source = models.CharField(max_length=50, blank=True, null=True)
    phage = models.ForeignKey(phage, on_delete=models.DO_NOTHING)

    class Meta:
        db_table = 'phage_lifestyle'
        verbose_name = 'phage_lifestyle'
        verbose_name_plural = verbose_name

    def __str__(self):

        return self.lifestyle
