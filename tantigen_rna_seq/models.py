from django.db import models

class tantigen_rna_seq(models.Model):
    agacc = models.TextField(blank=True, null=True)
    antigen_name = models.CharField(max_length=20, blank=True, null=True)
    seq_5 = models.TextField(blank=True, null=True)
    cds = models.TextField(blank=True, null=True)
    seq_3 = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'tantigen_rna_seq'
        verbose_name = 'tantigen_rna_seq'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.agacc