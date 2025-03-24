from django.db import models

class Schedule(models.Model):
    生産日 = models.TextField(blank=True, null=True)
    ワーク = models.BigIntegerField(blank=True, null=True)
    品番 = models.TextField(blank=True, null=True)
    製品名 = models.TextField(blank=True, null=True)
    生産数 = models.BigIntegerField(blank=True, null=True)
    縦 = models.BigIntegerField(blank=True, null=True)
    横 = models.BigIntegerField(blank=True, null=True)
    色 = models.TextField(blank=True, null=True)
    その他 = models.BigIntegerField(blank=True, null=True)
    id = models.AutoField(primary_key=True)  
     
    class Meta:
        managed = False
        db_table = 'schedule2'  
        app_label = 'schedule'
        