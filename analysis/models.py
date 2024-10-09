from django.db import models


class analysis(models.Model):
    name = models.CharField(max_length=30,blank=True, null=True)
    mid = models.IntegerField(blank=True, null=True)
    description = models.CharField(max_length=30,blank=True, null=True)
    analysis_category = models.CharField(max_length=30,blank=True, null=True)
    cover_image = models.CharField(max_length=30,blank=True, null=True)
    documentation = models.TextField(blank=True, null=True)
    hidden = models.BooleanField(blank=True, null=True)
    task_demo_id = models.IntegerField(blank=True, null=True)
    demo_result_id = models.IntegerField(blank=True, null=True)


    class Meta:
        db_table = 'analysis'  
        verbose_name = 'analysis' 
        verbose_name_plural = verbose_name  

    def __str__(self):

        return self.name
