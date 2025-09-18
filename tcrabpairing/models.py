from django.db import models

class tcrabpairing(models.Model):
    source = models.CharField(max_length=200, blank=True, null=True) # GSM6063507_230093_primary_focus_filtered_contig_annotations
    barcode = models.CharField(max_length=300, blank=True, null=True)
    Alpha = models.CharField(max_length=400, blank=True, null=True) 
    Beta = models.CharField(max_length=400, blank=True, null=True) 
    umisA = models.FloatField(blank=True, null=True)
    umisB = models.FloatField(blank=True, null=True)
    clonotype_freq = models.IntegerField(blank=True, null=True)	
    TRAV = models.CharField(max_length=200, blank=True, null=True)
    TRAJ = models.CharField(max_length=200, blank=True, null=True)
    cdr3A = models.CharField(max_length=300, blank=True, null=True)
    cdr3_ntA = models.CharField(max_length=400, blank=True, null=True)
    readsA = models.IntegerField(blank=True, null=True)
    TRBV = models.CharField(max_length=200, blank=True, null=True)
    TRBJ = models.CharField(max_length=200, blank=True, null=True)
    cdr3B = models.CharField(max_length=300, blank=True, null=True)
    cdr3_ntB = models.CharField(max_length=400, blank=True, null=True)
    readsB = models.IntegerField(blank=True, null=True)
    raw_clonotype_id = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        db_table = 'tcrabpairing'
        verbose_name = 'tcrabpairing'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return str(self.id)
    