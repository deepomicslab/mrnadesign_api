from django.db import models

class antigen(models.Model):
    antigen_name = models.CharField(max_length=200, blank=True, null=True)
    antigen_aequence = models.CharField(max_length=20, blank=True, null=True)
    db_info = models.TextField(blank=True, null=True)
    sequence = models.TextField(blank=True, null=True)
    antigen_type = models.CharField(max_length=20, blank=True, null=True)
    model_structure = models.CharField(max_length=20, blank=True, null=True)
    href2 = models.TextField(max_length=500, blank=True, null=True)
    surface_access = models.CharField(max_length=20, blank=True, null=True)
    href3 = models.TextField(max_length=500, blank=True, null=True)
    protein_class = models.CharField(max_length=100, blank=True, null=True)
    database_reference1 = models.CharField(max_length=20, blank=True, null=True)
    href4 = models.TextField(max_length=500, blank=True, null=True)
    database_reference2 = models.CharField(max_length=20, blank=True, null=True)
    href5 = models.TextField(max_length=500, blank=True, null=True)
    database_reference3 = models.CharField(max_length=20, blank=True, null=True)
    href6 = models.TextField(max_length=500, blank=True, null=True) 
    source_organism = models.CharField(max_length=200, blank=True, null=True)
    href7 = models.TextField(max_length=500, blank=True, null=True)
    literature_reference = models.CharField(max_length=20, blank=True, null=True)
    href8 = models.TextField(max_length=500, blank=True, null=True)

    class Meta:
        db_table = 'antigen'
        verbose_name = 'antigen'
        verbose_name_plural = verbose_name

    def __str__(self):

        return self.antigen_name
