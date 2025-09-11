from django.db import models

class transcripthub_assembly(models.Model):
    organism = models.CharField(max_length=200, blank=True, null=True)
    record = models.CharField(max_length=200, blank=True, null=True) # GTEX-XXX-XXX-XX-XXXXX
    seqname = models.CharField(max_length=200, blank=True, null=True)
    source = models.CharField(max_length=200, blank=True, null=True)
    feature = models.CharField(max_length=200, blank=True, null=True)
    start = models.IntegerField(blank=True, null=True)
    end = models.IntegerField(blank=True, null=True)    
    score = models.FloatField(blank=True, null=True)
    strand = models.CharField(max_length=5, blank=True, null=True)
    frame = models.CharField(max_length=5, blank=True, null=True)
    attribute = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'transcripthub_assembly'
        verbose_name = 'transcripthub_assembly'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return str(self.id)
    
class transcripthub_annotation(models.Model):
    organism = models.CharField(max_length=200, blank=True, null=True)
    record = models.CharField(max_length=200, blank=True, null=True) # GTEX-XXX-XXX-XX-XXXXX
    seqname = models.CharField(max_length=200, blank=True, null=True)
    source = models.CharField(max_length=200, blank=True, null=True)
    feature = models.CharField(max_length=200, blank=True, null=True)
    start = models.IntegerField(blank=True, null=True)
    end = models.IntegerField(blank=True, null=True)    
    score = models.FloatField(blank=True, null=True)
    strand = models.CharField(max_length=5, blank=True, null=True)
    frame = models.CharField(max_length=5, blank=True, null=True)
    attribute = models.TextField(blank=True, null=True)
    genome_sequence = models.ForeignKey('genome_seq', on_delete=models.SET_NULL, blank=True, null=True, related_name='transcripts')


    class Meta:
        db_table = 'transcripthub_annotation'
        verbose_name = 'transcripthub_annotation'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return str(self.id)

class genome_seq(models.Model):
    seqname = models.CharField(max_length=200, blank=True, null=True)
    sequence = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'genome_seq'
        verbose_name = 'genome_seq'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return str(self.id)
    
