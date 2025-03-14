from django.db import models


class Samples(models.Model):
    name = models.CharField(max_length=255, unique=True)  # 对应sampleID（GTex sample meta table中）
    tissue_type = models.CharField(max_length=255, blank=True, null=True)  # 组织类型（GTex SMTS in sample meta table）
    tissue_type_detail = models.CharField(max_length=255, blank=True, null=True)  # 组织类型详细信息（GTex SMTSD in sample meta table）
    subject_id = models.CharField(max_length=255, blank=True, null=True)  # 对应SUBJID（GTex annotation meta table中）
    gender = models.IntegerField()  # 性别SEX（GTex annotation meta table中）
    min_age = models.IntegerField(null=True)  # 年龄AGE下限（GTex annotation meta table中）
    max_age = models.IntegerField(null=True)  # 年龄AGE上限（GTex annotation meta table中）
    death_circumstances = models.CharField(max_length=255, blank=True, null=True)  # 死亡情况DTHHRDY（GTex annotation meta table中）
    dataset_id = models.IntegerField()  # dataset 关联外键
    dataset_name = models.CharField(max_length=255)

    class Meta:
        db_table = 'samples'
        verbose_name = 'samples'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name
