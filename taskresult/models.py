from django.db import models
from django.contrib.postgres.fields import ArrayField


class lineardesign_taskresult(models.Model):
    mrna_task_analysis_type = models.CharField(max_length=60) # mrna_task.analysis_type
    task_id = models.IntegerField() # mrna_task.id

    seq_name = models.CharField(max_length=500)
    sequence = models.TextField()
    structure = models.TextField()
    folding_free_energy = models.FloatField()
    cai = models.FloatField()

    class Meta:
        db_table = 'lineardesign_taskresult'
        verbose_name = 'lineardesign_taskresult'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.id

class prediction_taskresult(models.Model):
    mrna_task_analysis_type = models.CharField(max_length=60) # mrna_task.analysis_type
    task_id = models.IntegerField() # mrna_task.id
    task_name = models.CharField() # user customised name

    class Meta:
        db_table = 'prediction_taskresult'
        verbose_name = 'prediction_taskresult'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.id
