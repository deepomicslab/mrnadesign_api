from django.db import models
from django.contrib.postgres.fields import HStoreField
from django.contrib.postgres.fields import ArrayField

class mrna_task(models.Model):
    id = models.AutoField(primary_key=True) # task id
    job_id = models.CharField(max_length=300) # slurm job id
    user_id = models.CharField(max_length=300)
    user_input_path = HStoreField() # dict
    is_demo_input = models.BooleanField()
    output_result_path = models.CharField(max_length=500)
    output_log_path = models.CharField(max_length=500)
    analysis_type = models.CharField(max_length=60)
    parameters =  HStoreField() # dict
    status = models.CharField(max_length=60)
    created_at = models.DateTimeField(auto_now_add=True)

    subtasks = ArrayField(models.IntegerField(), blank=True, null=True) # for prediction task, save the protein_score task ids

    class Meta:
        db_table = 'mrna_task'
        verbose_name = 'mrna_task'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.user_id+'_taskid_'+str(self.id)
