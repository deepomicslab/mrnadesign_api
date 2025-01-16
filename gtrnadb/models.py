from django.db import models


class gtrnadb_genome(models.Model):
    domain = models.CharField(max_length=200, blank=True, null=True)
    genome = models.CharField(max_length=300)
    genomeid = models.CharField(max_length=200)
    gtrnadb_url = models.CharField(max_length=500, blank=True, null=True)
    tax_id = models.CharField(max_length=100, blank=True, null=True)
    genbank_common_name = models.CharField(
        max_length=200, blank=True, null=True)
    scientific_name = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        db_table = 'gtrnadb_genome'
        verbose_name = 'gtrnadb_genome'
        verbose_name_plural = verbose_name

    def __str__(self):

        return self.genome


class gtrnadb_data(models.Model):
    # foreign key between this and gtrnadb_genome
    genomeid = models.CharField(max_length=200)

    gtrnadb_id = models.CharField(max_length=200)
    trna_scan_id = models.CharField(max_length=200, blank=True, null=True)
    trna_scan_id_code = models.CharField(max_length=200, blank=True, null=True)
    chr = models.CharField(max_length=200, blank=True, null=True)
    start = models.CharField(max_length=100, blank=True, null=True)
    end = models.CharField(max_length=100, blank=True, null=True)
    strand = models.CharField(max_length=100, blank=True, null=True)
    isotype = models.CharField(max_length=200, blank=True, null=True)
    anticodon = models.CharField(max_length=200, blank=True, null=True)
    intron_count = models.IntegerField(blank=True, null=True)
    mismatches = models.IntegerField(blank=True, null=True)
    score = models.FloatField(blank=True, null=True)
    pseudogene = models.IntegerField(blank=True, null=True)
    ids = models.CharField(max_length=300)
    length = models.IntegerField(blank=True, null=True)
    len_mature = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'gtrnadb_data'
        verbose_name = 'gtrnadb_data'
        verbose_name_plural = verbose_name

    def __str__(self):

        return self.genomeid + '_' + self.GtRNAdbID
