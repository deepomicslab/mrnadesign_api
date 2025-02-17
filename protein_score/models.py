from django.db import models
from django.contrib.postgres.fields import ArrayField

class protein_score(models.Model):
    seq = models.TextField() 

    seq_acc = models.CharField()
    overall_gc = models.FloatField(blank=True, null=True)
    codon_usage_efficiency_index = models.FloatField(blank=True, null=True)
    tis = models.FloatField(blank=True, null=True)
    rna_interference = models.IntegerField(blank=True, null=True)
    rna_structure = models.IntegerField(blank=True, null=True)
    ires_number = models.IntegerField(blank=True, null=True)
    degscore = models.FloatField(blank=True, null=True)

    class Meta:
        db_table = 'protein_score'
        verbose_name = 'protein_score'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.id
    

# 之后有 protein seq 的表（antigen，tantigen，tsnadb*）需要加一个 protein_score field