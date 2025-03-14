from django.db import models

class Datasets(models.Model):
    name = models.CharField(max_length=255, unique=True)
    database = models.CharField(max_length=255, blank=True, null=True)
    data_type = models.CharField(max_length=255, blank=True, null=True)
    submission_date = models.DateField(auto_now_add=True)
    last_update_date = models.DateField(auto_now=True)

    class Meta:
        db_table = 'datasets'
        verbose_name = 'datasets'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name
