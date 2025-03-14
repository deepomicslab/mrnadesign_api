from django.db import models


class ExpressionRecord(models.Model):
    gene_id = models.IntegerField() # gene 关联外键
    gene_id_str = models.CharField(max_length=200, blank=True, null=True)
    transcript_id = models.IntegerField() # transcript 关联外键
    transcript_id_str = models.CharField(max_length=200, blank=True, null=True)
    sample_id = models.IntegerField()  # sample 关联外键
    sample_id_str = models.CharField(max_length=200, blank=True, null=True)
    cov = models.FloatField(null=True)
    fpkm = models.FloatField(null=True)
    tpm = models.FloatField(null=True)

    class Meta:
        db_table = 'expression_record'
        verbose_name = 'expression_record'
        verbose_name_plural = verbose_name
        constraints = [
            models.UniqueConstraint(fields=['sample_id', 'transcript_id'], name='unique_sample_transcript')
        ]

    def __str__(self):
        return f"{self.sample_id_str}:{self.gene_id_str}|{self.transcript_id_str}"
